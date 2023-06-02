from random import randint
from datetime import timedelta, datetime
from django.db import models

from api.v1.apps.companies.models import AbstractIncomeExpense, Company
from api.v1.apps.companies.services import text_normalize
from api.v1.apps.companies.validators import uzb_phone_number_validation

from .services import firm_logo_upload_location, EskizUz


class Firm(models.Model):
    name = models.CharField(max_length=400)
    send_sms_name = models.CharField(max_length=400, blank=True)
    not_transfer_debt = models.IntegerField(default=0)
    transfer_debt = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    director = models.ForeignKey('accounts.CustomUser', related_name='firms', on_delete=models.PROTECT)
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    phone_number1 = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    phone_number2 = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    phone_number3 = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    logo = models.ImageField(upload_to=firm_logo_upload_location, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)
    desc = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.send_sms_name = ''.join([i for i in self.name if i.isalpha() or i.isdigit() or i in ' \''])
        self.name = text_normalize(self.name)
        self.address = text_normalize(self.address)
        self.desc = text_normalize(self.desc)
        super().save(*args, **kwargs)


class FirmIncome(AbstractIncomeExpense):
    transfer_type = None
    shift = None

    from_firm = models.ForeignKey(Firm, on_delete=models.PROTECT)
    deadline_date = models.DateField(blank=True, null=True)
    remaining_debt = models.IntegerField()
    is_paid = models.BooleanField(default=False)
    is_transfer_return = models.BooleanField(default=True)

    def __str__(self):
        return str(self.from_firm)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_debt = self.price
        super().save(*args, **kwargs)

        firm_report, _ = FirmReport.objects.get_or_create(income_id=self.id)
        firm_report.is_expense = False
        firm_report.creator_id = self.creator_id
        firm_report.firm_id = self.from_firm_id
        firm_report.created_at = self.created_at
        firm_report.report_date = self.report_date
        firm_report.price = self.price
        firm_report.is_transfer = self.is_transfer_return
        firm_report.save()


class FirmExpense(AbstractIncomeExpense):
    from_pharmacy_transfer = models.BooleanField(default=False)
    to_firm = models.ForeignKey(Firm, on_delete=models.PROTECT)
    from_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    is_verified = models.BooleanField(default=False)
    verified_code = models.PositiveIntegerField()
    verified_phone_number = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    verified_firm_worker_name = models.CharField(max_length=50, blank=True)

    from_user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.PROTECT, blank=True, null=True, related_name='firm_expenses')

    def __str__(self):
        return str(self.to_firm)

    def save(self, *args, **kwargs):
        FirmExpense.objects.filter(
            is_verified=False, created_at__lt=datetime.now() - timedelta(minutes=5)).delete()

        self.verified_firm_worker_name = text_normalize(self.verified_firm_worker_name).title()

        if not self.pk:
            self.verified_code = randint(10000, 99999)

            # send sms
            if not self.from_pharmacy_transfer:
                w_name = ''.join([i for i in self.verified_firm_worker_name if i.isalpha() or i in ' \''])
                try:
                    message = EskizUz.verify_code_message(
                        verify_code=self.verified_code, firm_name=self.to_firm.send_sms_name,
                        pharmacy_name=self.from_pharmacy.send_sms_name, price=self.price, firm_worker_name=w_name
                    )
                    EskizUz.send_sms(phone_number=self.verified_phone_number[1:], message=message)
                except Exception as e:
                    return e
            # ----------------------
            else:
                self.is_verified = True
        super().save(*args, **kwargs)

        if self.is_verified:
            incomes = self.to_firm.firmincome_set.filter(is_paid=False).order_by('created_at')
            temp_price = self.price
            for income in incomes:
                if temp_price > 0:
                    if income.remaining_debt <= temp_price:
                        income.is_paid = True
                        income.remaining_debt = 0
                        temp_price -= income.remaining_debt
                    else:
                        income.remaining_debt -= temp_price
                        temp_price = 0
                    income.save()
                else:
                    break
            if temp_price > 0:
                firm_debt, _ = FirmDebtByDate.objects.get_or_create(
                    firm_id=self.to_firm_id, report_date=self.report_date)
                if self.transfer_type == 1:
                    firm_debt.expenses_not_transfer_debt_price += temp_price
                else:
                    firm_debt.expenses_transfer_debt_price += temp_price
                firm_debt.save()

            firm_report, _ = FirmReport.objects.get_or_create(expense_id=self.id)
            firm_report.creator_id = self.creator_id
            firm_report.firm_id = self.to_firm_id
            firm_report.pharmacy_id = self.from_pharmacy_id
            firm_report.verified_phone_number = self.verified_phone_number
            firm_report.verified_firm_worker_name = self.verified_firm_worker_name
            firm_report.created_at = self.created_at
            firm_report.report_date = self.report_date
            firm_report.price = self.price
            firm_report.is_transfer = bool(self.transfer_type_id != 1)
            firm_report.save()


class FirmReturnProduct(AbstractIncomeExpense):
    transfer_type = None
    shift = None

    firm_income = models.ForeignKey(FirmIncome, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    verified_code = models.PositiveIntegerField()
    verified_phone_number = models.CharField(max_length=13, validators=[uzb_phone_number_validation])
    verified_firm_worker_name = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        self.verified_firm_worker_name = text_normalize(self.verified_firm_worker_name).title()

        if not self.pk:
            self.verified_code = randint(10000, 99999)

            # send sms
            w_name = ''.join([i for i in self.verified_firm_worker_name if i.isalpha() or i in ' \''])
            try:
                message = EskizUz.return_product_verify_code_message(
                    verify_code=self.verified_code, price=self.price, firm_worker_name=w_name,
                    firm_name=self.firm_income.from_firm.send_sms_name,
                    company_name=Company.objects.get(director_id=self.creator.director_id).name
                )
                EskizUz.send_sms(phone_number=self.verified_phone_number[1:], message=message)
            except Exception as e:
                return e

        super().save(*args, **kwargs)

        if self.is_verified:
            self.firm_income.remaining_debt -= self.price
            if self.firm_income.remaining_debt == 0:
                self.firm_income.is_paid = True
            self.firm_income.save()

            firm_report, _ = FirmReport.objects.get_or_create(return_product_id=self.id)
            firm_report.creator_id = self.creator_id
            firm_report.firm_id = self.firm_income.from_firm_id
            firm_report.verified_phone_number = self.verified_phone_number
            firm_report.verified_firm_worker_name = self.verified_firm_worker_name
            firm_report.created_at = self.created_at
            firm_report.report_date = self.report_date
            firm_report.price = self.price
            firm_report.is_transfer = self.firm_income.is_transfer_return
            firm_report.save()


class FirmDebtByMonth(models.Model):
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE, null=True)
    year = models.IntegerField()
    month = models.IntegerField()
    expense_price = models.IntegerField(default=0)
    income_price = models.IntegerField(default=0)


class FirmDebtByDate(models.Model):
    incomes_transfer_debt_price = models.IntegerField(default=0)
    incomes_not_transfer_debt_price = models.IntegerField(default=0)
    expenses_transfer_debt_price = models.IntegerField(default=0)
    expenses_not_transfer_debt_price = models.IntegerField(default=0)
    transfer_debt = models.IntegerField()
    not_transfer_debt = models.IntegerField()
    report_date = models.DateField()
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.transfer_debt = self.incomes_transfer_debt_price - self.expenses_transfer_debt_price
        self.not_transfer_debt = self.incomes_not_transfer_debt_price - self.expenses_not_transfer_debt_price
        super().save(*args, **kwargs)
        obj = FirmDebtByDate.objects.filter(firm_id=self.firm_id).order_by('-report_date').first()
        self.firm.transfer_debt = obj.transfer_debt
        self.firm.not_transfer_debt = obj.not_transfer_debt
        self.firm.save()


class FirmReport(models.Model):
    income = models.ForeignKey(FirmIncome, on_delete=models.CASCADE, blank=True, null=True)
    expense = models.ForeignKey(FirmExpense, on_delete=models.CASCADE, blank=True, null=True)
    return_product = models.ForeignKey(FirmReturnProduct, on_delete=models.CASCADE, blank=True, null=True)

    is_expense = models.BooleanField(default=True)
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE, null=True)
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.SET_NULL, null=True)
    verified_phone_number = models.CharField(max_length=13, blank=True)
    verified_firm_worker_name = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(null=True)
    report_date = models.DateField(null=True)
    price = models.IntegerField(default=0)
    is_transfer = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.firm and self.report_date:
            firm_debt, _ = FirmDebtByDate.objects.get_or_create(firm_id=self.firm_id, report_date=self.report_date)
            incomes_not_transfer_debt_price = FirmIncome.objects.filter(
                is_paid=False, is_transfer_return=False, from_firm_id=firm_debt.firm_id,
                report_date__lte=firm_debt.report_date).aggregate(s=models.Sum('remaining_debt'))['s']
            incomes_transfer_debt_price = FirmIncome.objects.filter(
                is_paid=False, is_transfer_return=True, from_firm_id=firm_debt.firm_id,
                report_date__lte=firm_debt.report_date).aggregate(s=models.Sum('remaining_debt'))['s']

            incomes_not_transfer_debt_price = incomes_not_transfer_debt_price if incomes_not_transfer_debt_price else 0
            incomes_transfer_debt_price = incomes_transfer_debt_price if incomes_transfer_debt_price else 0

            firm_debt.incomes_not_transfer_debt_price = incomes_not_transfer_debt_price
            firm_debt.incomes_transfer_debt_price = incomes_transfer_debt_price
            firm_debt.save()

            by_month, _ = FirmDebtByMonth.objects.get_or_create(
                month=self.report_date.month, year=self.report_date.year, firm_id=self.firm_id, pharmacy=self.pharmacy)

            expense_price = FirmReport.objects.filter(
                report_date__year=by_month.year,
                report_date__month=by_month.month,
                firm_id=by_month.firm_id,
                pharmacy=by_month.pharmacy,
                is_expense=True
            ).aggregate(s=models.Sum('price'))['s']

            income_price = FirmReport.objects.filter(
                report_date__year=by_month.year,
                report_date__month=by_month.month,
                firm_id=by_month.firm_id,
                pharmacy=by_month.pharmacy,
                is_expense=False
            ).aggregate(s=models.Sum('price'))['s']
            by_month.expense_price = expense_price if expense_price else 0
            by_month.income_price = income_price if income_price else 0
            by_month.save()

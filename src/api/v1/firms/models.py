from random import randint
from datetime import date
from django.db import models

from api.v1.companies.enums import DefaultTransferType
from api.v1.companies.models import AbstractIncomeExpense, Company
from api.v1.companies.services import text_normalize
from api.v1.pharmacies.services import get_worker_report_date
from api.v1.companies.validators import uzb_phone_number_validation

from .services import firm_logo_upload_location, EskizUz


class Firm(models.Model):
    name = models.CharField(max_length=400)
    is_favorite = models.BooleanField(default=False)
    send_sms_name = models.CharField(max_length=400, blank=True)
    not_transfer_debt = models.IntegerField(default=0)
    transfer_debt = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    director = models.ForeignKey('accounts.CustomUser', related_name='firms', on_delete=models.CASCADE)
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

    class Meta:
        unique_together = ['director', 'name']


class FirmIncome(AbstractIncomeExpense):
    shift = None
    transfer_type = None

    from_firm = models.ForeignKey(Firm, on_delete=models.CASCADE)
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


class FirmExcessExpense(models.Model):
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE)
    firm_expense = models.ForeignKey('firms.FirmExpense', on_delete=models.CASCADE)
    firm_income = models.ForeignKey(FirmIncome, on_delete=models.SET_NULL, null=True)
    report_date = models.DateField()
    price = models.IntegerField()
    remaining_price = models.IntegerField(default=0)
    is_transfer = models.BooleanField()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_price = self.price
        super().save(*args, **kwargs)


class FirmExpense(AbstractIncomeExpense):
    from_pharmacy_transfer = models.BooleanField(default=False)
    to_firm = models.ForeignKey(Firm, on_delete=models.CASCADE)
    from_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.SET_NULL, null=True)
    is_verified = models.BooleanField(default=False)
    verified_code = models.PositiveIntegerField()
    verified_phone_number = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    verified_firm_worker_name = models.CharField(max_length=50, blank=True)

    from_user = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, blank=True, null=True,
                                  related_name='firm_expenses')

    def __str__(self):
        return str(self.to_firm)

    def save(self, *args, **kwargs):
        if not self.pk:
            # if self.from_pharmacy and self.creator.is_worker:
            #     self.report_date = get_worker_report_date(self.from_pharmacy.last_shift_end_hour)
            # else:
            #     self.report_date = date.today()

            self.verified_firm_worker_name = text_normalize(self.verified_firm_worker_name).title()
            self.verified_code = randint(10000, 99999)
            # send sms
            if not self.from_pharmacy_transfer:
                w_name = ''.join([i for i in self.verified_firm_worker_name if i.isalpha() or i in ' \''])
                try:
                    message = EskizUz.verify_code_message(verify_code=self.verified_code,
                                                          firm_name=self.to_firm.send_sms_name,
                                                          pharmacy_name=self.from_pharmacy.send_sms_name,
                                                          price=self.price,
                                                          firm_worker_name=w_name)
                    EskizUz.send_sms(phone_number=self.verified_phone_number[1:], message=message)
                except Exception as e:
                    return e
            # ----------------------
            else:
                self.is_verified = True
        super().save(*args, **kwargs)

        if self.is_verified:
            if self.transfer_type_id == DefaultTransferType.cash.value:
                incomes = self.to_firm.firmincome_set.filter(is_paid=False, is_transfer_return=False
                                                             ).order_by('created_at')
            else:
                incomes = self.to_firm.firmincome_set.filter(is_paid=False, is_transfer_return=True
                                                             ).order_by('created_at')
            temp_price = self.price
            for income in incomes:
                if temp_price <= 0:
                    break

                if income.remaining_debt <= temp_price:
                    income.is_paid = True
                    income.remaining_debt = 0
                    temp_price -= income.remaining_debt
                else:
                    income.remaining_debt -= temp_price
                    temp_price = 0
                income.save()

            if temp_price > 0:
                FirmExcessExpense.objects.create(firm_expense_id=self.id,
                                                 firm_id=self.to_firm_id,
                                                 report_date=self.report_date,
                                                 price=temp_price,
                                                 is_transfer=bool(
                                                     self.transfer_type_id != DefaultTransferType.cash.value)
                                                 )

            firm_report, _ = FirmReport.objects.get_or_create(expense_id=self.id)
            firm_report.creator = self.creator
            firm_report.firm_id = self.to_firm_id
            firm_report.pharmacy = self.from_pharmacy
            firm_report.verified_phone_number = self.verified_phone_number
            firm_report.verified_firm_worker_name = self.verified_firm_worker_name
            firm_report.created_at = self.created_at
            firm_report.report_date = self.report_date
            firm_report.price = self.price
            firm_report.is_transfer = bool(self.transfer_type_id != DefaultTransferType.cash.value)
            firm_report.save()


class FirmReturnProduct(AbstractIncomeExpense):
    shift = None
    transfer_type = None

    firm_income = models.ForeignKey(FirmIncome, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    verified_code = models.PositiveIntegerField()
    verified_phone_number = models.CharField(max_length=13, validators=[uzb_phone_number_validation])
    verified_firm_worker_name = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.verified_firm_worker_name = text_normalize(self.verified_firm_worker_name).title()
            self.verified_code = randint(10000, 99999)

            # send sms
            w_name = ''.join([i for i in self.verified_firm_worker_name if i.isalpha() or i in ' \''])
            try:
                firm = self.firm_income.from_firm
                message = EskizUz.return_product_verify_code_message(verify_code=self.verified_code,
                                                                     price=self.price,
                                                                     firm_worker_name=w_name,
                                                                     firm_name=firm.send_sms_name,
                                                                     company_name=Company.objects.get(
                                                                         director_id=firm.director_id).name)

                EskizUz.send_sms(phone_number=self.verified_phone_number[1:], message=message)
            except Exception as e:
                print(e)
                return e

        super().save(*args, **kwargs)

        if self.is_verified:
            self.firm_income.remaining_debt -= self.price
            if self.firm_income.remaining_debt == 0:
                self.firm_income.is_paid = True
            self.firm_income.save()

            firm_report, _ = FirmReport.objects.get_or_create(return_product_id=self.id)
            firm_report.creator = self.creator
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
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.SET_NULL, null=True)
    year = models.IntegerField()
    month = models.IntegerField()
    expense_price = models.IntegerField(default=0)
    income_price = models.IntegerField(default=0)


class FirmDebtByDate(models.Model):
    transfer_debt = models.IntegerField(default=0)
    not_transfer_debt = models.IntegerField(default=0)

    report_date = models.DateField()
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            obj = FirmDebtByDate.objects.filter(firm_id=self.firm_id).order_by('-report_date', '-id').first()
            self.firm.transfer_debt = obj.transfer_debt
            self.firm.not_transfer_debt = obj.not_transfer_debt
            self.firm.save()
        except AttributeError:
            pass


class FirmReport(models.Model):
    income = models.ForeignKey(FirmIncome, on_delete=models.CASCADE, blank=True, null=True)
    expense = models.ForeignKey(FirmExpense, on_delete=models.CASCADE, blank=True, null=True)
    return_product = models.ForeignKey(FirmReturnProduct, on_delete=models.CASCADE, blank=True, null=True)

    firm = models.ForeignKey(Firm, on_delete=models.CASCADE, null=True)
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    is_expense = models.BooleanField(default=True)
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

            incomes_not_transfer_debt_price = FirmReport.objects.filter(firm_id=firm_debt.firm_id,
                                                                        is_expense=False,
                                                                        is_transfer=False,
                                                                        report_date__lte=firm_debt.report_date
                                                                        ).aggregate(s=models.Sum('price'))['s']

            incomes_transfer_debt_price = FirmReport.objects.filter(firm_id=firm_debt.firm_id,
                                                                    is_expense=False,
                                                                    is_transfer=True,
                                                                    report_date__lte=firm_debt.report_date
                                                                    ).aggregate(s=models.Sum('price'))['s']

            expenses_not_transfer_debt_price = FirmReport.objects.filter(firm_id=firm_debt.firm_id,
                                                                         is_expense=True,
                                                                         is_transfer=False,
                                                                         report_date__lte=firm_debt.report_date
                                                                         ).aggregate(s=models.Sum('price'))['s']

            expenses_transfer_debt_price = FirmReport.objects.filter(firm_id=firm_debt.firm_id,
                                                                     is_expense=True,
                                                                     is_transfer=True,
                                                                     report_date__lte=firm_debt.report_date
                                                                     ).aggregate(s=models.Sum('price'))['s']

            incomes_not_transfer_debt_price = incomes_not_transfer_debt_price if incomes_not_transfer_debt_price else 0
            incomes_transfer_debt_price = incomes_transfer_debt_price if incomes_transfer_debt_price else 0
            expenses_not_transfer_debt_price = expenses_not_transfer_debt_price if expenses_not_transfer_debt_price else 0
            expenses_transfer_debt_price = expenses_transfer_debt_price if expenses_transfer_debt_price else 0

            firm_debt.not_transfer_debt = incomes_not_transfer_debt_price - expenses_not_transfer_debt_price
            firm_debt.transfer_debt = incomes_transfer_debt_price - expenses_transfer_debt_price
            firm_debt.save()

            by_month, _ = FirmDebtByMonth.objects.get_or_create(month=self.report_date.month,
                                                                year=self.report_date.year,
                                                                firm_id=self.firm_id,
                                                                pharmacy=self.pharmacy)

            expense_price = FirmReport.objects.filter(report_date__year=by_month.year,
                                                      report_date__month=by_month.month,
                                                      firm_id=by_month.firm_id,
                                                      pharmacy=by_month.pharmacy,
                                                      is_expense=True
                                                      ).aggregate(s=models.Sum('price'))['s']

            by_month.expense_price = expense_price if expense_price else 0
            by_month.save()

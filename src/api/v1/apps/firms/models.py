from random import randint
from django.db import models
from datetime import timedelta, datetime

from api.v1.apps.companies.services import text_normalize
from api.v1.apps.companies.validators import uzb_phone_number_validation
from api.v1.apps.companies.models import AbstractIncomeExpense

from .services import firm_logo_upload_location, EskizUz


class Firm(models.Model):
    name = models.CharField(max_length=400)
    send_sms_name = models.CharField(max_length=400, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    transfer_debt = models.IntegerField(default=0)
    not_transfer_debt = models.IntegerField(default=0)
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


class FirmDebtByDate(models.Model):
    price = models.IntegerField(default=0)
    report_date = models.DateField()
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE)


class FirmIncome(AbstractIncomeExpense):
    transfer_type = None

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

        firm_report.creator_id = self.creator_id
        firm_report.firm_id = self.from_firm_id
        firm_report.created_at = self.created_at
        firm_report.report_date = self.report_date
        firm_report.price = self.price
        firm_report.is_transfer = self.is_transfer_return
        firm_report.save()

        not_transfer_debt = FirmIncome.objects.filter(
            is_paid=False, is_transfer_return=False, from_firm_id=self.from_firm_id
        ).aggregate(s=models.Sum('remaining_debt'))['s']
        transfer_debt = FirmIncome.objects.filter(
            is_paid=False, is_transfer_return=True, from_firm_id=self.from_firm_id
        ).aggregate(s=models.Sum('remaining_debt'))['s']
        not_transfer_debt = not_transfer_debt if not_transfer_debt else 0
        transfer_debt = transfer_debt if transfer_debt else 0
        firm = Firm.objects.get(id=self.from_firm_id)
        firm.not_transfer_debt = not_transfer_debt
        firm.transfer_debt = transfer_debt
        firm.save()

        obj, _ = FirmDebtByDate.objects.get_or_create(report_date=self.report_date, firm_id=self.from_firm_id)
        obj.price = not_transfer_debt + transfer_debt
        obj.save()


class FirmExpense(AbstractIncomeExpense):
    from_pharmacy_transfer = models.BooleanField(default=False)
    to_firm = models.ForeignKey(Firm, on_delete=models.PROTECT)
    from_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    is_verified = models.BooleanField(default=False)
    verified_code = models.PositiveIntegerField()
    verified_phone_number = models.CharField(max_length=13, validators=[uzb_phone_number_validation])
    verified_firm_worker_name = models.CharField(max_length=50)

    from_user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.PROTECT, blank=True, null=True, related_name='firm_expenses'
    )

    def __str__(self):
        return str(self.to_firm)

    def save(self, *args, **kwargs):
        self.verified_firm_worker_name = text_normalize(self.verified_firm_worker_name).title()

        FirmExpense.objects.filter(
            is_verified=False, created_at__lt=datetime.now() - timedelta(minutes=5)).delete()

        if not self.pk:
            self.verified_code = randint(10000, 99999)

            # incomes remaining debt update
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
                firm = Firm.objects.get(id=self.to_firm_id)
                if self.from_pharmacy_transfer:
                    firm.transfer_debt -= temp_price
                else:
                    firm.not_transfer_debt -= temp_price
                firm.save()

                obj, _ = FirmDebtByDate.objects.get_or_create(report_date=self.report_date, firm_id=self.to_firm_id)
                obj.price -= temp_price
                obj.save()
            # ----------------------------

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
                    print(e)
            # ----------------------
        super().save(*args, **kwargs)
        firm_report, _ = FirmReport.objects.get_or_create(expense_id=self.id)
        firm_report.creator_id = self.creator_id
        firm_report.firm_id = self.to_firm_id
        firm_report.created_at = self.created_at
        firm_report.report_date = self.report_date
        firm_report.price = self.price
        firm_report.is_transfer = self.from_pharmacy_transfer
        firm_report.pharmacy_id = self.from_pharmacy_id
        firm_report.verified_phone_number = self.verified_phone_number
        firm_report.verified_firm_worker_name = self.verified_firm_worker_name
        firm_report.save()


class FirmReport(models.Model):
    income = models.ForeignKey(FirmIncome, on_delete=models.CASCADE, blank=True, null=True)
    expense = models.ForeignKey(FirmExpense, on_delete=models.CASCADE, blank=True, null=True)

    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE, null=True)
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.SET_NULL, null=True)
    verified_phone_number = models.CharField(max_length=13, blank=True)
    verified_firm_worker_name = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(null=True)
    report_date = models.DateField(null=True)
    price = models.IntegerField(default=0)
    is_transfer = models.BooleanField(default=False)

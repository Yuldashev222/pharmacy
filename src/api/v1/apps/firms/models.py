from random import randint
from django.db import models
from datetime import date, timedelta, datetime
from django.core.validators import MinValueValidator

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


class FirmIncome(AbstractIncomeExpense):
    transfer_type = None

    from_firm = models.ForeignKey(Firm, on_delete=models.PROTECT)
    deadline_date = models.DateField(validators=[MinValueValidator(date.today())], blank=True, null=True)
    remaining_debt = models.IntegerField()
    is_paid = models.BooleanField(default=False)
    is_transfer_return = models.BooleanField(default=True)

    def __str__(self):
        return str(self.from_firm)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_debt = self.price
        super().save(*args, **kwargs)
        FirmReport.objects.create(income_id=self.id)

        not_transfer_debt = FirmIncome.objects.filter(
            is_paid=False, is_transfer_return=False, from_firm_id=self.from_firm_id
        ).aggregate(s=models.Sum('remaining_debt'))['s']
        transfer_debt = FirmIncome.objects.filter(
            is_paid=False, is_transfer_return=True, from_firm_id=self.from_firm_id
        ).aggregate(s=models.Sum('remaining_debt'))['s']

        obj = Firm.objects.get(id=self.from_firm_id)
        obj.not_transfer_debt = not_transfer_debt if not_transfer_debt else 0
        obj.transfer_debt = transfer_debt if transfer_debt else 0
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
            is_verified=False, created_at__lt=datetime.now() - timedelta(minutes=5)
        ).delete()

        if not self.pk:
            self.verified_code = randint(10000, 99999)

            # incomes remaining debt update
            incomes = self.to_firm.firmincome_set.filter(is_paid=False).order_by('created_at')
            temp_price = self.price
            i = 0
            while temp_price > 0:
                income = incomes[i]
                i += 1
                if income.remaining_debt <= temp_price:
                    income.is_paid = True
                    income.remaining_debt = 0
                    temp_price -= income.remaining_debt
                else:
                    income.remaining_debt -= temp_price
                    temp_price = 0
                income.save()
            # ----------------------------

            # send sms
            if not self.from_pharmacy_transfer:
                w_name = ''.join([i for i in self.verified_firm_worker_name if i.isalpha() or i in ' \''])
                try:
                    message = EskizUz.verify_code_message(
                        verify_code=self.verified_code,
                        firm_name=self.to_firm.send_sms_name,
                        pharmacy_name=self.from_pharmacy.send_sms_name,
                        price=self.price,
                        firm_worker_name=w_name
                    )
                    EskizUz.send_sms(phone_number=self.verified_phone_number[1:], message=message)
                except Exception as e:
                    print(e)
            # ----------------------

        super().save(*args, **kwargs)
        FirmReport.objects.create(expense_id=self.id)


class FirmReport(models.Model):
    income = models.ForeignKey(FirmIncome, on_delete=models.CASCADE, blank=True, null=True)
    expense = models.ForeignKey(FirmExpense, on_delete=models.CASCADE, blank=True, null=True)

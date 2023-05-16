from random import randint
from django.db import models
from datetime import date, timedelta
from django.core.validators import MinValueValidator

from api.v1.apps.pharmacies.models import Pharmacy
from api.v1.apps.debts.models import DebtToPharmacy
from api.v1.apps.companies.services import text_normalize
from api.v1.apps.companies.validators import uzb_phone_number_validation
from api.v1.apps.companies.models import AbstractIncomeExpense

from .services import firm_logo_upload_location, EskizUz


class Firm(models.Model):
    name = models.CharField(max_length=400)
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
        self.name = text_normalize(self.name)
        self.address = text_normalize(self.address)
        self.desc = text_normalize(self.desc)
        super().save(*args, **kwargs)


class FirmIncome(AbstractIncomeExpense):
    transfer_type = None

    from_firm = models.ForeignKey(Firm, on_delete=models.PROTECT)
    to_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT)
    deadline_date = models.DateField(validators=[MinValueValidator(date.today())], blank=True, null=True)
    paid_on_time = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.from_firm)


class FirmExpense(models.Model):
    to_firm = models.ForeignKey(Firm, on_delete=models.PROTECT)
    from_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT)
    is_verified = models.BooleanField(default=False)
    verified_code = models.PositiveIntegerField()
    verified_phone_number = models.CharField(max_length=13, validators=[uzb_phone_number_validation])
    verified_firm_worker_name = models.CharField(max_length=50)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.verified_firm_worker_name = text_normalize(self.verified_firm_worker_name).title()
        if not self.pk:
            self.verified_code = randint(10000, 99999)
            # message = EskizUz.verify_code_message(
            #     verify_code=self.verified_code,
            #     firm_name=self.to_firm.name,
            #     pharmacy_name=kwargs['pharmacy_name'],
            #     price=kwargs['price_amount'],
            #     firm_worker_name=self.verified_firm_worker_name
            # )
            # status = EskizUz.send_sms(phone_number=self.verified_phone_number[1:], message=message)
            # if status == 200:  # last
            #     message = EskizUz.success_message(
            #         firm_worker_name=self.verified_firm_worker_name,
            #         price=kwargs['price_amount']
            #     )
            #     EskizUz.send_sms(phone_number=self.verified_phone_number[1:], message=message)
        super().save(*args, **kwargs)


class FirmFromPharmacyExpense(FirmExpense, AbstractIncomeExpense):
    from_user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.PROTECT,
        blank=True, null=True, related_name='firm_expenses'
    )

    def save(self, *args, **kwargs):
        FirmFromPharmacyExpense.objects.filter(
            is_verified=False, created_at__lt=timedelta(minutes=5) + date.today()
        ).delete()
        kwargs['pharmacy_name'] = self.from_pharmacy.name
        kwargs['price_amount'] = self.price
        super().save(*args, **kwargs)


class FirmFromDebtExpense(FirmExpense, models.Model):
    from_pharmacy = None
    from_debt = models.ForeignKey(DebtToPharmacy, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        expenses = FirmFromDebtExpense.objects.filter(
            is_verified=False, from_debt__created_at__lt=timedelta(minutes=5) + date.today()
        )
        if expenses.exists():
            DebtToPharmacy.objects.filter(id__in=expenses.values_list('from_debt_id', flat=True).distinct()).delete()
            expenses.delete()
        kwargs['pharmacy_name'] = self.from_debt.to_pharmacy.name
        kwargs['price_amount'] = self.from_debt.price
        super().save(*args, **kwargs)

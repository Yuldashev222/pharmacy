from datetime import date
from django.db import models
from django.core.validators import MinValueValidator

from api.v1.apps.companies.models import Company
from api.v1.apps.pharmacies.models import Pharmacy
from api.v1.apps.general.services import text_normalize
from api.v1.apps.general.validators import uzb_phone_number_validation
from api.v1.apps.general.models import AbstractIncomeExpense, TransferMoneyType

from .services import firm_logo_upload_location


class Firm(models.Model):
    name = models.CharField(max_length=400)
    # total_amount_purchased = models.PositiveIntegerField(default=0)
    # total_amount_given = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    phone_number1 = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    phone_number2 = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    phone_number3 = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    logo = models.ImageField(upload_to=firm_logo_upload_location, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)
    desc = models.CharField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        self.name = text_normalize(self.name)
        self.address = text_normalize(self.address)
        self.desc = text_normalize(self.desc)
        super().save(*args, **kwargs)


class FirmIncome(AbstractIncomeExpense):
    income_expense_type = None

    from_firm = models.ForeignKey(Firm, on_delete=models.PROTECT)
    to_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT)
    deadline_date = models.DateField(validators=[MinValueValidator(date.today())])
    paid_on_time = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)


class FirmExpense(AbstractIncomeExpense):
    to_firm_income = models.ForeignKey(FirmIncome, on_delete=models.PROTECT)  # to_firm
    from_pharmacy = models.BooleanField(default=True)
    is_transfer = models.BooleanField(default=False)
    transfer_type = models.ForeignKey(TransferMoneyType, on_delete=models.PROTECT,
                                      blank=True, null=True)

    is_verified = models.BooleanField(default=False)  # sms
    verified_code = models.PositiveIntegerField()
    verified_phone_number = models.CharField(max_length=13, validators=[uzb_phone_number_validation])
    verified_firm_worker_name = models.CharField(max_length=150, blank=True)

    def save(self, *args, **kwargs):
        self.verified_firm_worker_name = text_normalize(self.verified_firm_worker_name)
        super().save(*args, **kwargs)

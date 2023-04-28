from django.db import models

from api.v1.apps.companies.models import Company
from api.v1.apps.pharmacies.models import Pharmacy
from api.v1.apps.accounts.models import CustomUser
from api.v1.apps.general.models import AbstractIncomeExpense
from api.v1.apps.general.validators import uzb_phone_number_validation

from .services import firm_logo_upload_location


class Firm(models.Model):
    name = models.CharField(max_length=400)
    total_amount_purchased = models.PositiveIntegerField(default=0)
    total_amount_given = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)

    phone_number1 = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    phone_number2 = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    phone_number3 = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    logo = models.ImageField(upload_to=firm_logo_upload_location, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)
    desc = models.CharField(max_length=500, blank=True)


class FirmIncome(AbstractIncomeExpense):
    income_expense_type, to_firm, to_user = (None,) * 3
    from_firm = models.ForeignKey(Firm, on_delete=models.PROTECT)
    to_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT)
    term_date = models.DateField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    desc = models.CharField(max_length=500, blank=True)


class FirmExpense(AbstractIncomeExpense):
    to_user = None
    to_firm = models.ForeignKey(Firm, on_delete=models.PROTECT)

    # select
    from_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT,
                                      blank=True, null=True)
    from_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,
                                  null=True, blank=True)
    desc = models.CharField(max_length=500, blank=True)
    # ------

    is_verified = models.BooleanField(default=False)
    verified_code = models.PositiveIntegerField()
    verified_phone_number = models.CharField(max_length=13, validators=[uzb_phone_number_validation])
    verified_firm_worker_name = models.CharField(max_length=150, blank=True)

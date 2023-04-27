from django.db import models

from api.v1.apps.companies.models import Company
from api.v1.apps.accounts.models import CustomUser
from api.v1.apps.general.validators import uzb_phone_number_validation

from .services import firm_logo_upload_location


class Firm(models.Model):
    name = models.CharField(max_length=400)
    total_amount_purchased = models.PositiveIntegerField(default=0)
    total_amount_given = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)

    phone_number = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    logo = models.ImageField(upload_to=firm_logo_upload_location, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)
    desc = models.CharField(max_length=500, blank=True)

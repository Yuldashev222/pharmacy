from django.db import models

from api.v1.apps.general.validators import uzb_phone_number_validation

from .services import company_logo_upload_location


class Company(models.Model):
    name = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    director = models.ForeignKey('accounts.CustomUser', related_name='pharmacies', on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    logo = models.ImageField(upload_to=company_logo_upload_location, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)
    desc = models.TextField(max_length=1000, blank=True)
    phone_number = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

from django.db import models

from api.v1.apps.general.services import text_normalize
from api.v1.apps.general.validators import uzb_phone_number_validation

from .services import company_logo_upload_location


class Company(models.Model):
    name = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    director = models.OneToOneField('accounts.CustomUser', related_name='companies', on_delete=models.CASCADE)

    logo = models.ImageField(upload_to=company_logo_upload_location, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)
    desc = models.TextField(max_length=1000, blank=True)
    phone_number = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = text_normalize(self.name)
        self.address = text_normalize(self.address)
        self.desc = text_normalize(self.desc)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

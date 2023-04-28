from django.db import models

from api.v1.apps.companies.models import Company

from .services import pharmacy_logo_upload_location


class Pharmacy(models.Model):
    name = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company, related_name='pharmacies', on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    logo = models.ImageField(upload_to=pharmacy_logo_upload_location, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)
    desc = models.TextField(max_length=1000, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Pharmacy'
        verbose_name_plural = 'Pharmacies'

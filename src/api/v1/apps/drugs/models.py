from django.db import models

from api.v1.apps.accounts.models import CustomUser
from api.v1.apps.pharmacies.models import Pharmacy
from api.v1.apps.companies.services import text_normalize


class Drug(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=150)
    price = models.IntegerField(blank=True, null=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    desc = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.name = text_normalize(self.name)
        self.manufacturer = text_normalize(self.manufacturer)
        self.desc = text_normalize(self.desc)
        super().save(*args, **kwargs)

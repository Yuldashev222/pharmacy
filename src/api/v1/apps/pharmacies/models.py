from django.db import models

from api.v1.apps.companies.services import text_normalize

from .services import pharmacy_logo_upload_location


class Pharmacy(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    director = models.ForeignKey('accounts.CustomUser', related_name='pharmacies', on_delete=models.PROTECT)
    logo = models.ImageField(upload_to=pharmacy_logo_upload_location, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)
    desc = models.TextField(max_length=1000, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = text_normalize(self.name)
        self.address = text_normalize(self.address)
        self.desc = text_normalize(self.desc)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Pharmacy'
        verbose_name_plural = 'Pharmacies'


class Check(models.Model):
    price = models.IntegerField(default=0)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    report_date = models.DateField()
    shift = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ['pharmacy', 'shift', 'pharmacy']

    def __str__(self):
        return str(self.price)

from django.db import models


class AllPharmacyIncomeReportMonth(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    price = models.IntegerField(default=0)
    receipt_price = models.IntegerField(default=0)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)


class AllReturnProductReportMonth(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    price = models.IntegerField(default=0)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)

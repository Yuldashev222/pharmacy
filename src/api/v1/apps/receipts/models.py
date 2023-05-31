from django.db import models

from api.v1.apps.incomes.models import PharmacyIncomeReportDay, PharmacyIncomeReportMonth
from api.v1.apps.pharmacies.models import Pharmacy


class Receipt(models.Model):
    price = models.IntegerField(default=0)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    report_date = models.DateField()
    shift = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ['pharmacy', 'shift', 'report_date']

    def __str__(self):
        return str(self.price)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        obj = PharmacyIncomeReportDay.objects.get_or_create(
            pharmacy_id=self.pharmacy_id, report_date=self.report_date)[0]
        receipt_price = Receipt.objects.filter(
            report_date=obj.report_date, pharmacy_id=obj.pharmacy_id).aggregate(s=models.Sum('price'))['s']

        obj.receipt_price = receipt_price if receipt_price else 0
        obj.save()

from django.db import models

from api.v1.incomes.models import PharmacyIncomeReportDay
from api.v1.pharmacies.models import Pharmacy, PharmacyReportByShift


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

        obj, _ = PharmacyIncomeReportDay.objects.get_or_create(pharmacy_id=self.pharmacy_id,
                                                               report_date=self.report_date)

        receipt_price = Receipt.objects.filter(report_date=obj.report_date,
                                               pharmacy_id=obj.pharmacy_id
                                               ).aggregate(s=models.Sum('price'))['s']

        obj.receipt_price = receipt_price if receipt_price else 0
        obj.save()

        obj, _ = PharmacyReportByShift.objects.get_or_create(pharmacy_id=self.pharmacy_id,
                                                             report_date=self.report_date,
                                                             shift=self.shift)

        obj.receipt_price = self.price
        obj.save()

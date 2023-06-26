from django.db import models

from api.v1.pharmacies.models import Pharmacy, PharmacyReportByShift


class Receipt(models.Model):
    price = models.BigIntegerField(default=0)
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
        obj, _ = PharmacyReportByShift.objects.get_or_create(pharmacy_id=self.pharmacy_id,
                                                             report_date=self.report_date,
                                                             shift=self.shift)

        obj.receipt_price = self.price
        obj.save()

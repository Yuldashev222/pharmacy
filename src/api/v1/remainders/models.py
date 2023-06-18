from datetime import datetime
from django.db import models

from api.v1.pharmacies.models import PharmacyReportByShift


class RemainderShift(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE)
    report_date = models.DateField()
    shift = models.IntegerField()
    price = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.price = self.price if self.price >= 0 else 0
        super().save(*args, **kwargs)

        obj, _ = PharmacyReportByShift.objects.get_or_create(pharmacy_id=self.pharmacy_id,
                                                             shift=self.shift,
                                                             report_date=self.report_date)

        obj.remainder = self.price
        obj.save()


class RemainderDetail(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE, null=True)
    debt_to_pharmacy = models.ForeignKey('debts.DebtToPharmacy', on_delete=models.CASCADE, null=True)
    debt_from_pharmacy = models.ForeignKey('debts.DebtFromPharmacy', on_delete=models.CASCADE, null=True)
    user_expense = models.ForeignKey('expenses.UserExpense', on_delete=models.CASCADE, null=True)
    pharmacy_expense = models.ForeignKey('expenses.PharmacyExpense', on_delete=models.CASCADE, null=True)
    firm_expense = models.ForeignKey('firms.FirmExpense', on_delete=models.CASCADE, null=True)
    pharmacy_income = models.ForeignKey('incomes.PharmacyIncome', on_delete=models.CASCADE, null=True)
    debt_repay_from_pharmacy = models.ForeignKey('debts.DebtRepayFromPharmacy', on_delete=models.CASCADE, null=True)
    debt_repay_to_pharmacy = models.ForeignKey('debts.DebtRepayToPharmacy', on_delete=models.CASCADE, null=True)

    report_date = models.DateField(null=True)
    price = models.IntegerField(default=0)
    shift = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.report_date and self.shift and self.pharmacy:
            price = RemainderDetail.objects.filter(pharmacy_id=self.pharmacy_id,
                                                   report_date=self.report_date,
                                                   shift=self.shift
                                                   ).aggregate(s=models.Sum('price'))['s']

            obj, _ = RemainderShift.objects.get_or_create(pharmacy_id=self.pharmacy_id,
                                                          shift=self.shift,
                                                          report_date=self.report_date)
            obj.price = price if price else 0

            old_obj = RemainderShift.objects.filter(id__lt=obj.id,
                                                    pharmacy_id=obj.pharmacy_id,
                                                    shift=obj.shift,
                                                    report_date=obj.report_date).order_by('-id')
            if old_obj.exists():
                old_price = old_obj.first().price
                obj.price += old_price
            obj.save()

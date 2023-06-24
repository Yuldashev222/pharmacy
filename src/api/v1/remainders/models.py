from django.db import models

from api.v1.pharmacies.models import PharmacyReportByShift

from .tasks import update_all_next_remainders


class RemainderShift(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE)
    report_date = models.DateField()
    shift = models.IntegerField()
    price = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        obj, _ = PharmacyReportByShift.objects.get_or_create(pharmacy_id=self.pharmacy_id,
                                                             shift=self.shift,
                                                             report_date=self.report_date)

        obj.remainder = self.price
        obj.save()

    @classmethod
    def get_price(cls, pharmacy_id, report_date, shift):
        objs = cls.objects.filter(pharmacy_id=pharmacy_id, report_date=report_date, shift__lte=shift).order_by('-shift')
        if objs.exists():
            return objs.first().price
        objs = cls.objects.filter(pharmacy_id=pharmacy_id, report_date__lt=report_date).order_by('-report_date',
                                                                                                 '-shift')
        if objs.exists():
            return objs.first().price

        return 0


class RemainderDetail(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE, null=True)
    debt_to_pharmacy = models.ForeignKey('debts.DebtToPharmacy', on_delete=models.CASCADE, null=True)
    debt_from_pharmacy = models.ForeignKey('debts.DebtFromPharmacy', on_delete=models.CASCADE, null=True)
    debt_repay_from_pharmacy = models.ForeignKey('debts.DebtRepayFromPharmacy', on_delete=models.CASCADE, null=True)
    debt_repay_to_pharmacy = models.ForeignKey('debts.DebtRepayToPharmacy', on_delete=models.CASCADE, null=True)
    user_expense = models.ForeignKey('expenses.UserExpense', on_delete=models.CASCADE, null=True)
    pharmacy_expense = models.ForeignKey('expenses.PharmacyExpense', on_delete=models.CASCADE, null=True)
    firm_expense = models.ForeignKey('firms.FirmExpense', on_delete=models.CASCADE, null=True)
    pharmacy_income = models.ForeignKey('incomes.PharmacyIncome', on_delete=models.CASCADE, null=True)

    report_date = models.DateField(null=True)
    price = models.IntegerField(default=0)
    shift = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.report_date and self.shift and self.pharmacy:
            obj, _ = RemainderShift.objects.get_or_create(pharmacy_id=self.pharmacy_id,
                                                          shift=self.shift,
                                                          report_date=self.report_date)

            price = RemainderDetail.objects.filter(pharmacy_id=obj.pharmacy_id,
                                                   report_date=obj.report_date,
                                                   shift__lte=obj.shift
                                                   ).aggregate(s=models.Sum('price'))['s']
            price = price if price else 0

            price2 = RemainderDetail.objects.filter(pharmacy_id=obj.pharmacy_id,
                                                    report_date__lt=obj.report_date,
                                                    ).aggregate(s=models.Sum('price'))['s']
            price += price2 if price2 else 0

            obj.price = price
            obj.save()

            update_all_next_remainders.delay(obj.pharmacy_id, str(obj.report_date), obj.shift)

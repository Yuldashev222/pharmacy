from django.db import models

from api.v1.apps.accounts.models import WorkerReport
from api.v1.apps.companies.models import TransferMoneyType, AbstractIncomeExpense
from api.v1.apps.companies.reports.models import AllPharmacyIncomeReportMonth


class PharmacyIncomeReportMonth(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    year = models.IntegerField()
    month = models.IntegerField()
    price = models.IntegerField(default=0)
    receipt_price = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.pharmacy}: {self.price}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        obj, _ = AllPharmacyIncomeReportMonth.objects.get_or_create(year=self.year, month=self.month,
                                                                    director_id=self.pharmacy.director_id)
        data = PharmacyIncomeReportMonth.objects.filter(month=obj.month).aggregate(
            s=models.Sum('price'), rs=models.Sum('receipt_price'))

        price, receipt_price = data['s'], data['rs']
        obj.price = price if price else 0
        obj.receipt_price = receipt_price if receipt_price else 0
        obj.save()


class PharmacyIncomeReportDay(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    report_date = models.DateField()
    price = models.IntegerField(default=0)
    receipt_price = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.pharmacy}: {self.price}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        obj, _ = PharmacyIncomeReportMonth.objects.get_or_create(
            pharmacy_id=self.pharmacy_id, year=self.report_date.year, month=self.report_date.month)

        data = PharmacyIncomeReportDay.objects.filter(
            report_date__month=obj.month, pharmacy_id=obj.pharmacy_id
        ).aggregate(s=models.Sum('price'), rs=models.Sum('receipt_price'))

        price, receipt_price = data['s'], data['rs']
        obj.price = price if price else 0
        obj.receipt_price = receipt_price if receipt_price else 0
        obj.save()


class PharmacyIncome(AbstractIncomeExpense):
    to_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    to_user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.PROTECT, related_name='pharmacy_incomes', blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        obj, _ = PharmacyIncomeReportDay.objects.get_or_create(pharmacy_id=self.to_pharmacy_id,
                                                               report_date=self.report_date)
        price = PharmacyIncome.objects.filter(report_date=obj.report_date,
                                              to_pharmacy_id=obj.pharmacy_id
                                              ).aggregate(s=models.Sum('price'))['s']

        obj.price = price if price else 0
        obj.save()

    def __str__(self):
        return f'{self.to_pharmacy}: {self.price}'

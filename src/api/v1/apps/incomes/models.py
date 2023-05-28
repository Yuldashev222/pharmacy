from django.db import models

from api.v1.apps.accounts.reports.models import WorkerReport
from api.v1.apps.companies.reports.models import AllPharmacyIncomeReportMonth
from api.v1.apps.companies.models import TransferMoneyType, AbstractIncomeExpense


class PharmacyIncomeReportMonth(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    year = models.IntegerField()
    month = models.IntegerField()
    price = models.IntegerField(default=0)
    receipt_price = models.IntegerField(default=0)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.pharmacy}: {self.price}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = PharmacyIncomeReportMonth.objects.filter(month=self.month).aggregate(
            s=models.Sum('price'),
            rs=models.Sum('receipt_price')
        )
        price, receipt_price = data['s'], data['rs']
        obj = AllPharmacyIncomeReportMonth.objects.get_or_create(
            year=self.year,
            month=self.month,
            director_id=self.director_id
        )[0]
        obj.price = price if price else 0
        obj.receipt_price = receipt_price if receipt_price else 0
        obj.save()


class PharmacyIncomeReportDay(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    report_date = models.DateField()
    price = models.IntegerField(default=0)
    receipt_price = models.IntegerField(default=0)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.pharmacy}: {self.price}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = PharmacyIncomeReportDay.objects.filter(
            report_date__month=self.report_date.month,
            pharmacy_id=self.pharmacy_id
        ).aggregate(s=models.Sum('price'), rs=models.Sum('receipt_price'))
        price, receipt_price = data['s'], data['rs']
        obj = PharmacyIncomeReportMonth.objects.get_or_create(
            pharmacy_id=self.pharmacy_id, year=self.report_date.year,
            month=self.report_date.month, director_id=self.director_id
        )[0]
        obj.price = price if price else 0
        obj.receipt_price = receipt_price if receipt_price else 0
        obj.save()


class PharmacyIncome(AbstractIncomeExpense):
    to_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    to_user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.PROTECT,
        related_name='pharmacy_incomes', blank=True, null=True
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.to_user:
            obj, _ = WorkerReport.objects.get_or_create(pharmacy_income_id=self.id)
            obj.report_date = self.report_date,
            obj.price = self.price,
            obj.creator_id = self.creator_id,
            obj.worker_id = self.to_user_id,
            obj.created_at = self.created_at
            obj.is_expense = False
            obj.save()
        else:
            WorkerReport.objects.filter(pharmacy_income_id=self.id).delete()

        price = PharmacyIncome.objects.filter(
            report_date=self.report_date,
            to_pharmacy_id=self.to_pharmacy_id
        ).aggregate(s=models.Sum('price'))['s']
        obj = PharmacyIncomeReportDay.objects.get_or_create(
            pharmacy_id=self.to_pharmacy_id,
            report_date=self.report_date,
            director_id=self.creator.director_id
        )[0]
        obj.price = price if price else 0
        obj.save()

    def __str__(self):
        return f'{self.to_pharmacy}: {self.price}'

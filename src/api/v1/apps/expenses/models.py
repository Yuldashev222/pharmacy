from django.db import models

from api.v1.apps.accounts.reports.models import WorkerReport
from api.v1.apps.companies.enums import StaticEnv
from api.v1.apps.companies.services import text_normalize
from api.v1.apps.companies.models import AbstractIncomeExpense
from api.v1.apps.expenses.reports.models import ReturnProductReportMonth, DiscountProductReportMonth


class ExpenseType(models.Model):
    name = models.CharField(max_length=300)
    is_user_expense = models.BooleanField(default=False)
    desc = models.CharField(max_length=600, blank=True)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.desc = text_normalize(self.desc)
        self.name = text_normalize(self.name)
        super().save(*args, **kwargs)


class UserExpense(AbstractIncomeExpense):
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT)
    from_user = models.ForeignKey('accounts.CustomUser', on_delete=models.PROTECT, related_name='from_user_expenses')

    # select
    to_user = models.ForeignKey('accounts.CustomUser', on_delete=models.PROTECT,
                                related_name='to_user_expenses', null=True, blank=True)
    to_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT, null=True)  # last

    # -------

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        obj, _ = WorkerReport.objects.get_or_create(user_expense_id=self.id, worker_id=self.from_user_id)
        obj.report_date = self.report_date,
        obj.price = self.price,
        obj.creator = self.creator,
        obj.worker_id = self.from_user_id,
        obj.created_at = self.created_at
        obj.save()

        if self.to_user:
            obj, _ = WorkerReport.objects.get_or_create(user_expense_id=self.id, worker_id=self.to_user_id)
            obj.report_date = self.report_date,
            obj.price = self.price,
            obj.creator = self.creator,
            obj.worker_id = self.to_user_id,
            obj.created_at = self.created_at
            obj.is_expense = False
            obj.save()
        else:
            WorkerReport.objects.filter(user_expense_id=self.id, worker_id=self.to_user_id).delete()

    def __str__(self):
        return f'{self.expense_type}: {self.price}'


class PharmacyExpense(AbstractIncomeExpense):
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT)
    from_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    to_user = models.ForeignKey('accounts.CustomUser', on_delete=models.PROTECT,
                                related_name='pharmacy_expenses', null=True, blank=True)

    def __str__(self):
        return f'{self.expense_type}: {self.price}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.to_user:
            obj, _ = WorkerReport.objects.get_or_create(pharmacy_expense_id=self.id, worker_id=self.to_user_id)
            obj.report_date = self.report_date,
            obj.price = self.price,
            obj.creator = self.creator,
            obj.worker_id = self.to_user_id,
            obj.created_at = self.created_at
            obj.is_expense = False
            obj.save()
        else:
            WorkerReport.objects.filter(pharmacy_expense_id=self.id, worker_id=self.to_user_id).delete()

        if self.expense_type_id == StaticEnv.return_product_id.value:
            price = PharmacyExpense.objects.filter(
                from_pharmacy_id=self.from_pharmacy_id,
                report_date__year=self.report_date.year,
                report_date__month=self.report_date.month
            ).aggregate(s=models.Sum('price'))['s']
            obj = ReturnProductReportMonth.objects.get_or_create(
                pharmacy_id=self.from_pharmacy_id,
                year=self.report_date.year,
                month=self.report_date.month,
                director_id=self.from_pharmacy.director_id
            )[0]
            obj.price = price if price else 0
            obj.save()

        elif self.expense_type_id == StaticEnv.discount_id.value:
            price = PharmacyExpense.objects.filter(
                from_pharmacy_id=self.from_pharmacy_id,
                report_date__year=self.report_date.year,
                report_date__month=self.report_date.month
            ).aggregate(s=models.Sum('price'))['s']
            obj = DiscountProductReportMonth.objects.get_or_create(
                pharmacy_id=self.from_pharmacy_id,
                year=self.report_date.year,
                month=self.report_date.month,
                director_id=self.from_pharmacy.director_id
            )[0]
            obj.price = price if price else 0
            obj.save()

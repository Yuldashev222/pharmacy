from django.db import models

from api.v1.apps.companies.services import text_normalize
from api.v1.apps.companies.models import AbstractIncomeExpense
from api.v1.apps.expenses.reports.models import ExpenseReportMonth


class ExpenseType(models.Model):
    name = models.CharField(max_length=300)
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
    to_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE, blank=True, null=True)

    # -------

    def __str__(self):
        return f'{self.expense_type}: {self.price}'


class PharmacyExpense(AbstractIncomeExpense):
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT)
    from_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    to_user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.PROTECT, related_name='pharmacy_expenses', null=True, blank=True)

    def __str__(self):
        return f'{self.expense_type}: {self.price}'

    def save(self, *args, **kwargs):
        change = False
        if self.pk:
            expense_type_id = PharmacyExpense.objects.get(id=self.id).expense_type_id
            if expense_type_id != self.expense_type_id:
                change = True
        super().save(*args, **kwargs)
        if change:
            price = PharmacyExpense.objects.filter(from_pharmacy_id=self.from_pharmacy_id,
                                                   expense_type_id=expense_type_id,
                                                   report_date__year=self.report_date.year,
                                                   report_date__month=self.report_date.month
                                                   ).aggregate(s=models.Sum('price'))['s']
            obj, _ = ExpenseReportMonth.objects.get_or_create(pharmacy_id=self.from_pharmacy_id,
                                                              expense_type_id=expense_type_id,
                                                              year=self.report_date.year, month=self.report_date.month)
            obj.price = price if price else 0
            obj.save()

        price = PharmacyExpense.objects.filter(from_pharmacy_id=self.from_pharmacy_id,
                                               expense_type_id=self.expense_type_id,
                                               report_date__year=self.report_date.year,
                                               report_date__month=self.report_date.month
                                               ).aggregate(s=models.Sum('price'))['s']
        obj, _ = ExpenseReportMonth.objects.get_or_create(pharmacy_id=self.from_pharmacy_id,
                                                          expense_type_id=self.expense_type_id,
                                                          year=self.report_date.year,
                                                          month=self.report_date.month)
        obj.price = price if price else 0
        obj.save()

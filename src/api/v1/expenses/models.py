from django.db import models

from api.v1.accounts.models import CustomUser
from api.v1.companies.models import AbstractIncomeExpense
from api.v1.companies.services import text_normalize
from api.v1.expenses.reports.models import ExpenseReportMonth

from .enums import DefaultExpenseType


class ExpenseType(models.Model):
    name = models.CharField(max_length=300)
    desc = models.CharField(max_length=600, blank=True)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)

    @classmethod
    def get_default_expense(cls):
        return cls.objects.get_or_create(name='deleted', director_id=CustomUser.get_fake_director().id)[0]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.desc = text_normalize(self.desc)
        self.name = text_normalize(self.name)
        super().save(*args, **kwargs)


class UserExpense(AbstractIncomeExpense):
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.SET(ExpenseType.get_default_expense))
    to_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE)
    from_user = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True,
                                  related_name='from_user_expenses')

    to_user = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL,
                                related_name='to_user_expenses', null=True, blank=True)

    def __str__(self):
        return f'{self.expense_type}: {self.price}'


class PharmacyExpense(AbstractIncomeExpense):
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.SET(ExpenseType.get_default_expense))
    from_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE)
    to_user = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, related_name='pharmacy_expenses',
                                null=True, blank=True)

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
            obj, _ = ExpenseReportMonth.objects.get_or_create(pharmacy_id=self.from_pharmacy_id,
                                                              expense_type_id=expense_type_id,
                                                              year=self.report_date.year,
                                                              month=self.report_date.month)

            price = PharmacyExpense.objects.filter(from_pharmacy_id=obj.pharmacy_id,
                                                   expense_type_id=expense_type_id,
                                                   report_date__year=obj.year,
                                                   report_date__month=obj.month
                                                   ).aggregate(s=models.Sum('price'))['s']

            obj.price = price if price else 0

            if self.expense_type_id == DefaultExpenseType.discount_id.value:
                objs = PharmacyExpense.objects.filter(from_pharmacy_id=self.from_pharmacy_id,
                                                      expense_type_id=self.expense_type_id,
                                                      report_date__year=self.report_date.year,
                                                      report_date__month=self.report_date.month
                                                      ).values_list('second_name', flat=True)

                second_name_price = sum(list(map(lambda x: int(x) if str(x).isdigit() else 0, objs)))
                obj.second_name = str(second_name_price)

            obj.save()

        obj, _ = ExpenseReportMonth.objects.get_or_create(pharmacy_id=self.from_pharmacy_id,
                                                          expense_type_id=self.expense_type_id,
                                                          year=self.report_date.year,
                                                          month=self.report_date.month)

        price = PharmacyExpense.objects.filter(from_pharmacy_id=obj.pharmacy_id,
                                               expense_type_id=obj.expense_type_id,
                                               report_date__year=obj.year,
                                               report_date__month=obj.month
                                               ).aggregate(s=models.Sum('price'))['s']

        obj.price = price if price else 0

        if self.expense_type_id == DefaultExpenseType.discount_id.value:
            objs = PharmacyExpense.objects.filter(from_pharmacy_id=obj.pharmacy_id,
                                                  expense_type_id=self.expense_type_id,
                                                  report_date__year=obj.year,
                                                  report_date__month=obj.month
                                                  ).values_list('second_name', flat=True)

            second_name_price = sum(list(map(lambda x: int(x) if str(x).isdigit() else 0, objs)))
            obj.second_name = str(second_name_price)

        obj.save()

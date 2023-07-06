from django.db import models


class AllPharmacyIncomeReportMonth(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    price = models.BigIntegerField(default=0)
    receipt_price = models.BigIntegerField(default=0)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)


class AllExpenseReportMonth(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    price = models.BigIntegerField(default=0)
    expense_type = models.ForeignKey('expenses.ExpenseType', on_delete=models.CASCADE, null=True)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)

from django.db import models

from api.v1.apps.companies.reports.models import AllExpenseReportMonth


class ExpenseReportMonth(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    expense_type = models.ForeignKey('expenses.ExpenseType', on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    price = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        price = ExpenseReportMonth.objects.filter(month=self.month, expense_type_id=self.expense_type_id
                                                  ).aggregate(s=models.Sum('price'))['s']
        obj, _ = AllExpenseReportMonth.objects.get_or_create(year=self.year, month=self.month,
                                                             expense_type_id=self.expense_type_id,
                                                             director_id=self.pharmacy.director_id)
        obj.price = price if price else 0
        obj.save()

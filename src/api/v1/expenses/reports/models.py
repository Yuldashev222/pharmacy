from django.db import models

from api.v1.companies.reports.models import AllExpenseReportMonth


class ExpenseReportMonth(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE)
    expense_type = models.ForeignKey('expenses.ExpenseType', on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    price = models.BigIntegerField(default=0)
    second_name = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        obj, _ = AllExpenseReportMonth.objects.get_or_create(year=self.year,
                                                             month=self.month,
                                                             expense_type_id=self.expense_type_id,
                                                             director_id=self.pharmacy.director_id)

        price = ExpenseReportMonth.objects.filter(month=obj.month,
                                                  year=obj.year,
                                                  expense_type_id=obj.expense_type_id,
                                                  pharmacy__director_id=obj.director_id
                                                  ).aggregate(s=models.Sum('price'))['s']

        obj.price = price if price else 0
        obj.save()

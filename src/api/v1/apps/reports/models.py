from django.db import models


class Report(models.Model):
    """
    Daily Report
    """
    report_date = models.DateField(unique=True)
    total_amount_incomes = models.PositiveIntegerField(default=0)
    total_amount_expenses = models.PositiveIntegerField(default=0)
    total_amount_debt_trading = models.PositiveIntegerField(default=0)

    # datadan -> datagacha filter va jamisi
    # last

    def __str__(self):
        return str(self.report_date)

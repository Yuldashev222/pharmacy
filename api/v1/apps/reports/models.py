from django.db import models


class Report(models.Model):
    """
    Daily Report
    """
    report_date = models.DateField()
    total_amount_incomes = models.PositiveIntegerField(default=0)
    total_amount_expenses = models.PositiveIntegerField(default=0)
    total_amount_debt_trading = models.PositiveIntegerField(default=0)
    # datadan -> datagacha filter va jamisi
    # last

from django.db import models


class WorkerReportMonth(models.Model):
    worker = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    expense_price = models.IntegerField(default=0)
    income_price = models.IntegerField(default=0)


class WorkerReport(models.Model):
    is_expense = models.BooleanField(default=True)
    debt_repay_from_pharmacy = models.ForeignKey('debts.DebtRepayFromPharmacy', on_delete=models.CASCADE, null=True,
                                                 blank=True)
    user_expense = models.ForeignKey('expenses.UserExpense', on_delete=models.CASCADE, null=True, blank=True)
    pharmacy_expense = models.ForeignKey('expenses.PharmacyExpense', on_delete=models.CASCADE, null=True, blank=True)
    pharmacy_income = models.ForeignKey('incomes.PharmacyIncome', on_delete=models.CASCADE, null=True, blank=True)
    firm_expense = models.ForeignKey('firms.FirmExpense', on_delete=models.CASCADE, null=True, blank=True)

    report_date = models.DateField(null=True)
    price = models.IntegerField(default=0)
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='reports')
    worker = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        obj, _ = WorkerReportMonth.objects.get_or_create(
            report_date__month=self.report_date.month,
            report_date__year=self.report_date.year,
            worker_id=self.worker_id
        )
        expense_price, income_price = (
            WorkerReport.objects.filter(is_expense=True, report_date__year=obj.year, report_date__month=obj.month
                                        ).aggregate(s=models.Sum('price'))['s'],
            WorkerReport.objects.filter(is_expense=False, report_date__year=obj.year, report_date__month=obj.month
                                        ).aggregate(s=models.Sum('price'))['s']
        )
        obj.expense_price = expense_price if expense_price else 0
        obj.income_price = income_price if income_price else 0
        obj.save()
        super().save(*args, **kwargs)

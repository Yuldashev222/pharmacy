from datetime import datetime

from django.db import models


class Remainder(models.Model):
    debt_to_pharmacy = models.ForeignKey('debts.DebtToPharmacy', on_delete=models.CASCADE, blank=True, null=True)
    debt_repay_from_pharmacy = models.ForeignKey('debts.DebtRepayFromPharmacy', on_delete=models.CASCADE, blank=True,
                                                 null=True)
    debt_from_pharmacy = models.ForeignKey('debts.DebtFromPharmacy', on_delete=models.CASCADE, blank=True, null=True)
    debt_repay_to_pharmacy = models.ForeignKey('debts.DebtRepayToPharmacy', on_delete=models.CASCADE, blank=True,
                                               null=True)
    user_expense = models.ForeignKey('expenses.UserExpense', on_delete=models.CASCADE, blank=True, null=True)
    pharmacy_expense = models.ForeignKey('expenses.PharmacyExpense', on_delete=models.CASCADE, blank=True, null=True)
    firm_expense = models.ForeignKey('firms.FirmExpense', on_delete=models.CASCADE, blank=True, null=True)
    pharmacy_income = models.ForeignKey('incomes.PharmacyIncome', on_delete=models.CASCADE, blank=True, null=True)

    report_date = models.DateField(null=True)
    price = models.IntegerField(default=0)
    shift = models.IntegerField(null=True)
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE, null=True)

    @classmethod
    def get_price(cls, report_date, shift, pharmacy_id):
        try:
            report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
            shift = int(shift)
            pharmacy_id = int(pharmacy_id)
        except Exception as e:
            return 0

        shift -= 1
        if shift < 1:
            return 0
        price = cls.objects.filter(
            report_date=report_date, shift=shift, pharmacy_id=pharmacy_id).aggregate(s=models.Sum('price'))['s']
        return price if price else 0

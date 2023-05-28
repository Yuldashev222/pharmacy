from django.db import models

from api.v1.apps.accounts.reports.models import WorkerReport
from api.v1.apps.firms.models import FirmExpense
from api.v1.apps.expenses.models import UserExpense, PharmacyExpense
from api.v1.apps.companies.validators import uzb_phone_number_validation
from api.v1.apps.companies.models import AbstractIncomeExpense, TransferMoneyType


class DebtToPharmacy(AbstractIncomeExpense):  # aptekaga qarz berdi
    from_who = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=13, blank=True, validators=[uzb_phone_number_validation])
    to_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    to_firm_expense = models.ForeignKey(FirmExpense, on_delete=models.CASCADE, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    remaining_debt = models.IntegerField()
    user_expense = models.ForeignKey(UserExpense, on_delete=models.SET_NULL, blank=True, null=True)
    pharmacy_expense = models.ForeignKey(PharmacyExpense, on_delete=models.SET_NULL, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_debt = self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.from_who


class DebtRepayFromPharmacy(AbstractIncomeExpense):  # apteka qarzini qaytardi
    to_debt = models.ForeignKey(DebtToPharmacy, on_delete=models.CASCADE)
    from_user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.PROTECT, related_name='debt_repays', blank=True, null=True
    )

    def __str__(self):
        return str(self.to_debt)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.from_user:
            obj, _ = WorkerReport.objects.get_or_create(debt_repay_from_pharmacy_id=self.id)
            obj.report_date = self.report_date,
            obj.price = self.price,
            obj.creator_id = self.creator_id,
            obj.worker_id = self.from_user_id,
            obj.created_at = self.created_at
            obj.save()
        else:
            WorkerReport.objects.filter(debt_repay_from_pharmacy_id=self.id).delete()


class DebtFromPharmacy(AbstractIncomeExpense):  # apteka qarz berdi
    is_paid = models.BooleanField(default=False)
    is_client = models.BooleanField(default=True)
    from_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    to_who = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=13, blank=True, validators=[uzb_phone_number_validation])
    remaining_debt = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_debt = self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.to_who


class DebtRepayToPharmacy(AbstractIncomeExpense):  # aptekaga qarzini qaytardi
    from_debt = models.ForeignKey(DebtFromPharmacy, on_delete=models.PROTECT)

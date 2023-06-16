from django.db import models

from api.v1.firms.models import FirmExpense
from api.v1.expenses.models import UserExpense, PharmacyExpense
from api.v1.companies.validators import uzb_phone_number_validation
from api.v1.companies.models import AbstractIncomeExpense


class DebtToPharmacy(AbstractIncomeExpense):  # aptekaga qarz berdi
    to_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE)
    from_who = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=13, blank=True, validators=[uzb_phone_number_validation])
    is_paid = models.BooleanField(default=False)
    remaining_debt = models.IntegerField()

    # select
    user_expense = models.ForeignKey(UserExpense, on_delete=models.CASCADE, blank=True, null=True)
    to_firm_expense = models.ForeignKey(FirmExpense, on_delete=models.CASCADE, blank=True, null=True)
    pharmacy_expense = models.ForeignKey(PharmacyExpense, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_debt = self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.from_who


class DebtRepayFromPharmacy(AbstractIncomeExpense):  # apteka qarzini qaytardi
    to_debt = models.ForeignKey(DebtToPharmacy, on_delete=models.CASCADE)
    from_user = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, related_name='debt_repays',
                                  blank=True, null=True)

    def __str__(self):
        return str(self.to_debt)


class DebtFromPharmacy(AbstractIncomeExpense):  # apteka qarz berdi
    is_paid = models.BooleanField(default=False)
    is_client = models.BooleanField(default=True)
    from_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE)
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
    from_debt = models.ForeignKey(DebtFromPharmacy, on_delete=models.CASCADE)

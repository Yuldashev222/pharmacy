from django.db import models

from api.v1.accounts.models import CustomUser
from api.v1.companies.services import text_normalize

from .services import pharmacy_logo_upload_location


class Pharmacy(models.Model):
    name = models.CharField(max_length=100)
    send_sms_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    director = models.ForeignKey('accounts.CustomUser', related_name='pharmacies', on_delete=models.CASCADE)
    logo = models.ImageField(upload_to=pharmacy_logo_upload_location, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)
    desc = models.TextField(max_length=1000, blank=True)
    last_shift_end_hour = models.PositiveSmallIntegerField(default=0,
                                                           help_text='Is the branch open until 00:00? If not, '
                                                                     'enter what time the business day ends')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.send_sms_name = ''.join([i for i in self.name if i.isalpha() or i.isdigit() or i in ' \''])
        self.name = text_normalize(self.name)
        self.address = text_normalize(self.address)
        self.desc = text_normalize(self.desc)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['director', 'name']
        verbose_name = 'Pharmacy'
        verbose_name_plural = 'Pharmacies'


class PharmacyReportByShift(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    report_date = models.DateField()
    shift = models.IntegerField()
    worker = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    not_transfer_income = models.IntegerField(default=0)
    transfer_income = models.IntegerField(default=0)
    debt_income = models.IntegerField(default=0)
    total_expense = models.IntegerField(default=0)  # last
    remainder = models.IntegerField(default=0)
    receipt_price = models.IntegerField(default=0)
    transfer_discount_price = models.IntegerField(default=0)
    not_transfer_discount_price = models.IntegerField(default=0)

    expense_debt_repay_from_pharmacy = models.IntegerField(default=0)
    expense_debt_from_pharmacy = models.IntegerField(default=0)
    expense_pharmacy = models.IntegerField(default=0)
    expense_firm = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        try:
            self.worker = CustomUser.objects.get(shift=self.shift, is_main_worker=True, pharmacy_id=self.pharmacy_id)
        except CustomUser.DoesNotExist:
            pass

        self.total_expense = sum([self.expense_debt_repay_from_pharmacy,
                                  self.expense_debt_from_pharmacy,
                                  self.expense_pharmacy,
                                  self.expense_firm])

        super().save(*args, **kwargs)

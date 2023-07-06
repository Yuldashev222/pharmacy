from django.db import models

from api.v1.incomes.models import PharmacyIncomeReportMonth, PharmacyIncomeReportDay
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
    last_shift_end_hour = models.PositiveIntegerField(default=0,
                                                      help_text='Is the branch open until 00:00? If not, '
                                                                'enter what time the business day ends')
    is_favorite = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @classmethod
    def get_deleted_pharmacy_obj(cls, pharmacy_name):
        return cls.objects.get_or_create(name=f'deleted {str(pharmacy_name[:90]).replace("deleted", "")}',
                                         director_id=CustomUser.get_fake_director().id)[0]

    def save(self, *args, **kwargs):
        self.send_sms_name = ''.join([i for i in self.name if i.isalpha() or i.isdigit() or i in ' \''])
        self.name = text_normalize(self.name)
        self.address = text_normalize(self.address)
        self.desc = text_normalize(self.desc)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Pharmacy'
        verbose_name_plural = 'Pharmacies'


class PharmacyReportByShift(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    report_date = models.DateField()
    shift = models.IntegerField()
    worker = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    not_transfer_income = models.BigIntegerField(default=0)
    transfer_income = models.BigIntegerField(default=0)
    debt_income = models.BigIntegerField(default=0)
    total_expense = models.BigIntegerField(default=0)  # last
    remainder = models.BigIntegerField(default=0)
    receipt_price = models.BigIntegerField(default=0)
    transfer_discount_price = models.BigIntegerField(default=0)
    not_transfer_discount_price = models.BigIntegerField(default=0)
    total_income = models.BigIntegerField(default=0)

    expense_debt_repay_from_pharmacy = models.BigIntegerField(default=0)
    expense_debt_from_pharmacy = models.BigIntegerField(default=0)
    expense_pharmacy = models.BigIntegerField(default=0)
    expense_firm = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.total_income = sum(
            [
                self.not_transfer_income, self.transfer_income, self.debt_income, self.transfer_discount_price,
                self.not_transfer_discount_price
            ]
        )
        try:
            self.worker = CustomUser.objects.get(shift=self.shift, is_main_worker=True, pharmacy_id=self.pharmacy_id)
        except CustomUser.DoesNotExist:
            pass

        self.total_expense = sum([self.expense_debt_repay_from_pharmacy,
                                  self.expense_debt_from_pharmacy,
                                  self.expense_pharmacy,
                                  self.expense_firm])

        obj, _ = PharmacyIncomeReportDay.objects.get_or_create(pharmacy_id=self.pharmacy_id,
                                                               report_date=self.report_date)

        data = PharmacyReportByShift.objects.filter(report_date=obj.report_date,
                                                    pharmacy_id=obj.pharmacy_id
                                                    ).aggregate(total_income=models.Sum('total_income'),
                                                                receipt_price=models.Sum('receipt_price'))

        obj.price = data['total_income'] if data['total_income'] else 0
        obj.receipt_price = data['receipt_price'] if data['receipt_price'] else 0
        obj.save()

        obj, _ = PharmacyIncomeReportMonth.objects.get_or_create(pharmacy_id=self.pharmacy_id,
                                                                 year=self.report_date.year,
                                                                 month=self.report_date.month)

        data = PharmacyReportByShift.objects.filter(report_date__month=obj.month,
                                                    report_date__year=obj.year,
                                                    pharmacy_id=obj.pharmacy_id
                                                    ).aggregate(total_income=models.Sum('total_income'),
                                                                receipt_price=models.Sum('receipt_price'))

        obj.price = data['total_income'] if data['total_income'] else 0
        obj.receipt_price = data['receipt_price'] if data['receipt_price'] else 0
        obj.save()

        super().save(*args, **kwargs)

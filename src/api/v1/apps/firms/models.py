from random import randint
from django.db import models
from datetime import date, timedelta, datetime
from django.core.validators import MinValueValidator

from api.v1.apps.companies.services import text_normalize
from api.v1.apps.companies.validators import uzb_phone_number_validation
from api.v1.apps.companies.models import AbstractIncomeExpense

from .services import firm_logo_upload_location, EskizUz


class Firm(models.Model):
    name = models.CharField(max_length=400)
    created_at = models.DateTimeField(auto_now_add=True)
    director = models.ForeignKey('accounts.CustomUser', related_name='firms', on_delete=models.PROTECT)
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    phone_number1 = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    phone_number2 = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    phone_number3 = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)
    logo = models.ImageField(upload_to=firm_logo_upload_location, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)
    desc = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = text_normalize(self.name)
        self.address = text_normalize(self.address)
        self.desc = text_normalize(self.desc)
        super().save(*args, **kwargs)


class FirmIncome(AbstractIncomeExpense):
    transfer_type = None

    from_firm = models.ForeignKey(Firm, on_delete=models.PROTECT)
    to_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    deadline_date = models.DateField(validators=[MinValueValidator(date.today())], blank=True, null=True)
    remaining_debt = models.IntegerField(default=0)  # last
    is_paid = models.BooleanField(default=False)
    is_transfer_return = models.BooleanField(default=True)

    def __str__(self):
        return str(self.from_firm)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_debt = self.price
        super().save(*args, **kwargs)


class FirmExpense(AbstractIncomeExpense):
    from_pharmacy_transfer = models.BooleanField(default=False)
    to_firm = models.ForeignKey(Firm, on_delete=models.PROTECT)
    from_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    is_verified = models.BooleanField(default=False)
    verified_code = models.PositiveIntegerField()
    verified_phone_number = models.CharField(max_length=13, validators=[uzb_phone_number_validation])
    verified_firm_worker_name = models.CharField(max_length=50)

    from_user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.PROTECT, blank=True, null=True, related_name='firm_expenses'
    )

    def __str__(self):
        return str(self.to_firm)

    def save(self, *args, **kwargs):
        FirmExpense.objects.filter(
            is_verified=False, created_at__lt=datetime.now() - timedelta(minutes=5)
        ).delete()
        self.verified_firm_worker_name = text_normalize(self.verified_firm_worker_name).title()

        if not (self.pk or self.from_pharmacy_transfer):
            self.verified_code = randint(10000, 99999)
            verified_firm_worker_name = ' '.join([i for i in self.verified_firm_worker_name if i.isalpha()])
            incomes = self.to_firm.firmincome_set.filter(is_paid=False).order_by('created_at')
            temp_price = self.price
            for income in incomes:
                if temp_price > 0:
                    if income.price <= temp_price:
                        income.is_paid = True
                        temp_price -= income.price
                        income.remaining_debt = 0
                    else:
                        income.remaining_debt -= temp_price
                    income.save()

            try:
                firm_name = ' '.join([i for i in self.to_firm.name if i.isalpha()])
                pharmacy_name = ' '.join([i for i in self.from_pharmacy.name if i.isalpha()])

                message = EskizUz.verify_code_message(
                    verify_code=self.verified_code,
                    firm_name=firm_name,
                    pharmacy_name=pharmacy_name,
                    price=self.price,
                    firm_worker_name=verified_firm_worker_name
                )
                EskizUz.send_sms(phone_number=self.verified_phone_number[1:], message=message)
            except Exception as e:
                print(e)

        super().save(*args, **kwargs)


class FirmReport(models.Model):
    income = models.ForeignKey(FirmIncome, on_delete=models.CASCADE, blank=True, null=True)
    expense = models.ForeignKey(FirmExpense, on_delete=models.CASCADE, blank=True, null=True)
    firm_worker = models.CharField(max_length=50)
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE)
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE)
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    firm_worker_phone_number = models.CharField(max_length=13, blank=True)
    report_date = models.DateField()
    created_at = models.DateTimeField()
    price = models.IntegerField()
    is_transfer = models.BooleanField()

    def __str__(self):
        return str(self.firm)

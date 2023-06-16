from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser

from api.v1.companies.services import text_normalize
from api.v1.companies.validators import uzb_phone_number_validation

from .enums import UserRole
from .services import user_photo_upload_location
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['role']
    objects = CustomUserManager()

    phone_number = models.CharField(max_length=13, unique=True, validators=[uzb_phone_number_validation])
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(max_length=1, choices=UserRole.choices())
    is_main_worker = models.BooleanField(default=False)
    shift = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(3)])
    creator = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE, blank=True, null=True)
    director = models.ForeignKey('self', on_delete=models.CASCADE, related_name='employees', blank=True, null=True)
    wage = models.FloatField(validators=[MinValueValidator(0)], default=0)

    bio = models.CharField(max_length=500, blank=True)
    photo = models.ImageField(upload_to=user_photo_upload_location, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        self.first_name = text_normalize(self.first_name).title()
        self.last_name = text_normalize(self.last_name).title()
        self.bio = text_normalize(self.bio)
        self.address = text_normalize(self.address)
        super().save(*args, **kwargs)

    @property
    def is_project_owner(self):
        return self.role == UserRole.p.name

    @property
    def is_director(self):
        return self.role == UserRole.d.name

    @property
    def is_manager(self):
        return self.role == UserRole.m.name

    @property
    def is_worker(self):
        return self.role == UserRole.w.name


class WorkerReportMonth(models.Model):
    worker = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE, null=True)
    year = models.IntegerField()
    month = models.IntegerField()
    expense_price = models.IntegerField(default=0)
    income_price = models.IntegerField(default=0)


class WorkerReport(models.Model):
    is_expense = models.BooleanField(default=True)
    user_expense = models.ForeignKey('expenses.UserExpense', on_delete=models.CASCADE, null=True, blank=True)
    pharmacy_income = models.ForeignKey('incomes.PharmacyIncome', on_delete=models.CASCADE, null=True, blank=True)
    firm_expense = models.ForeignKey('firms.FirmExpense', on_delete=models.CASCADE, null=True, blank=True)
    debt_repay_from_pharmacy = models.ForeignKey('debts.DebtRepayFromPharmacy', on_delete=models.CASCADE,
                                                 null=True, blank=True)

    report_date = models.DateField(null=True)
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE, blank=True, null=True)
    price = models.IntegerField(default=0)
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='reports')
    worker = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(null=True)

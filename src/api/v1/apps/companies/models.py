from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import uzb_phone_number_validation
from .services import text_normalize, company_logo_upload_location


class TransferMoneyType(models.Model):
    name = models.CharField(max_length=150)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class AbstractIncomeExpense(models.Model):
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    report_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.PositiveIntegerField()
    shift = models.PositiveSmallIntegerField(validators=[MaxValueValidator(3), MinValueValidator(1)])
    transfer_type = models.ForeignKey(TransferMoneyType, on_delete=models.PROTECT)
    desc = models.CharField(max_length=500, blank=True)
    second_name = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        self.desc = text_normalize(self.desc)
        self.second_name = text_normalize(self.second_name)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Company(models.Model):
    name = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    director = models.OneToOneField('accounts.CustomUser', related_name='companies', on_delete=models.CASCADE)

    logo = models.ImageField(upload_to=company_logo_upload_location, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)
    desc = models.TextField(max_length=1000, blank=True)
    phone_number = models.CharField(max_length=13, validators=[uzb_phone_number_validation], blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = text_normalize(self.name)
        self.address = text_normalize(self.address)
        self.desc = text_normalize(self.desc)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

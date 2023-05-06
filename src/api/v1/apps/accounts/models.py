from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from api.v1.apps.firms.models import Firm
from api.v1.apps.companies.models import Company
from api.v1.apps.pharmacies.models import Pharmacy
from api.v1.apps.general.services import text_normalize
from api.v1.apps.general.validators import uzb_phone_number_validation

from .enums import UserRole
from .services import user_photo_upload_location
from .managers import CustomUserManager, WorkerManager, DirectorManager, ManagerManager


class CustomUser(AbstractUser):
    username = None
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['role']
    objects = CustomUserManager()

    phone_number = models.CharField(max_length=13, unique=True, validators=[uzb_phone_number_validation])
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(max_length=1, choices=UserRole.choices())
    shift = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(3)])
    creator = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=True, null=True)
    wage = models.FloatField(validators=[MinValueValidator(0)], default=0)

    bio = models.CharField(max_length=500, blank=True)
    photo = models.ImageField(upload_to=user_photo_upload_location, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        self.first_name = text_normalize(self.first_name)
        self.last_name = text_normalize(self.last_name)
        self.bio = text_normalize(self.bio)
        self.address = text_normalize(self.address)
        if self.is_worker:
            self.company_id = self.pharmacy.company_id
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

    def director_pharmacies_all(self):
        return Pharmacy.objects.filter(company__in=self.companies.all())

    def employee_pharmacies_all(self):
        return Pharmacy.objects.filter(company_id=self.company_id)

    def director_firms_all(self):
        return Firm.objects.filter(company__in=self.companies.all())

    def employee_firms_all(self):
        return Firm.objects.filter(company_id=self.company_id)


class Director(CustomUser):
    objects = DirectorManager()

    class Meta(CustomUser.Meta):
        proxy = True


class Manager(CustomUser):
    objects = ManagerManager()

    class Meta(CustomUser.Meta):
        proxy = True


class Worker(CustomUser):
    objects = WorkerManager()

    class Meta(CustomUser.Meta):
        proxy = True

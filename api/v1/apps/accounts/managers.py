from django.contrib.auth.models import UserManager
from django.contrib.auth.hashers import make_password


class CustomUserManager(UserManager):
    # def get_queryset(self):
    #     return super().get_queryset().exclude(role='p')

    def _create_user(self, phone_number, email, password, **extra_fields):
        if not phone_number:
            raise ValueError("The given phone_number must be set")
        email = self.normalize_email(email)
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, email, password, **extra_fields)

    def create_superuser(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, email, password, **extra_fields)


class DirectorManager(CustomUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(role='d')


class ManagerManager(CustomUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(role='m')


class WorkerManager(CustomUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(role='w')

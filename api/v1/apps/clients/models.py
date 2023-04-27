from django.core.validators import MinValueValidator
from django.db import models

from api.v1.apps.accounts.models import CustomUser
from api.v1.apps.accounts.services import user_photo_upload_location
from api.v1.apps.general.validators import uzb_phone_number_validation


class Client(models.Model):
    phone_number = models.CharField(max_length=13, unique=True, validators=[uzb_phone_number_validation])
    first_name = models.CharField("first name", max_length=150, blank=True)
    last_name = models.CharField("last name", max_length=150, blank=True)
    email = models.EmailField("email address", blank=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField("date created", auto_now_add=True)
    total_amount = models.FloatField(validators=[MinValueValidator(0)], default=0)

    bio = models.CharField(max_length=500, blank=True)
    photo = models.ImageField(upload_to=user_photo_upload_location, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)

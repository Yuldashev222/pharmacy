from django.db import models

from api.v1.accounts.models import CustomUser
from api.v1.companies.services import text_normalize
from api.v1.companies.validators import uzb_phone_number_validation


class Client(models.Model):
    phone_number1 = models.CharField(max_length=13, validators=[uzb_phone_number_validation])
    phone_number2 = models.CharField(max_length=13, blank=True, validators=[uzb_phone_number_validation])
    first_name = models.CharField("first name", max_length=150)
    last_name = models.CharField("last name", max_length=150, blank=True)
    email = models.EmailField("email address", blank=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    director = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='clients')
    created_at = models.DateTimeField("date created", auto_now_add=True)
    total_amount = models.PositiveBigIntegerField(default=0)

    bio = models.CharField(max_length=500, blank=True)
    birthdate = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)

    class Meta:
        unique_together = ['director', 'phone_number1']

    def save(self, *args, **kwargs):
        self.first_name = text_normalize(self.first_name)
        self.last_name = text_normalize(self.last_name)
        self.bio = text_normalize(self.bio)
        super().save(*args, **kwargs)

from django.db import models
from django.utils import timezone

from api.v1.apps.general.enums import Month


class Wage(models.Model):
    employee = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.CharField(max_length=3, choices=Month.choices())
    total_amount_expenses = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.year = timezone.now().year
            self.month = timezone.now().month
        super().save(*args, **kwargs)

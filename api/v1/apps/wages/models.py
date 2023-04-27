from django.db import models

from api.v1.apps.accounts.models import CustomUser

# class Wage(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

# total_amount_expenses = models.FloatField()

# def save(self, *args, **kwargs):
#     if not self.pk:
#         self.total_amount_expenses = Expense.objects \
#             .filter(to_user_id=self.user.id) \
#             .aggregate(pr=models.Count('price'))['pr']
#     super().save(*args, **kwargs)

import os

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from api.v1.apps.wages.models import Wage
from api.v1.apps.companies.models import Company

from .enums import UserRole
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def create_company(instance, created, *args, **kwargs):
    if created:
        if instance.role == UserRole.d.name:
            Company.objects.create(
                name=f'Company::{instance.first_name}-{instance.last_name}',
                director_id=instance.id
            )
        elif instance.role in [UserRole.m.name, UserRole.w.name]:
            Wage.objects.create(employee_id=instance.pk)


@receiver(post_delete, sender=CustomUser)
def delete_photo(instance, *args, **kwargs):
    # old_photo = CustomUser.objects.get(pk=obj.pk).logo
    if instance.photo and os.path.isfile(instance.photo.path):
        os.remove(instance.photo.path)  # last

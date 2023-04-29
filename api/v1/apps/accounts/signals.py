from django.db.models.signals import post_save
from django.dispatch import receiver

from api.v1.apps.companies.models import Company

from .enums import UserRole
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def create_company(instance, created, *args, **kwargs):
    if created and instance.role == UserRole.d.name:
        Company.objects.create(
            name=f'Company::{instance.first_name}-{instance.last_name}',
            director_id=instance.id
        )
    # instance.company_id = company.id  # last

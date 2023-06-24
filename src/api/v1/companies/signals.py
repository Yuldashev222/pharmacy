import os
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save

from .models import Company


@receiver(pre_save, sender=Company)
def create_company(instance, *args, **kwargs):
    if instance.pk:
        company = Company.objects.get(pk=instance.pk)
        if company.logo and company.logo != instance.logo:
            if os.path.isfile(company.logo.path):
                os.remove(company.logo.path)


@receiver(post_delete, sender=Company)
def delete_logo(instance, *args, **kwargs):
    if instance.logo and os.path.isfile(instance.logo.path):
        os.remove(instance.logo.path)

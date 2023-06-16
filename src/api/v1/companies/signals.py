import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .models import Company


@receiver(post_save, sender=Company)
def create_company(instance, created, *args, **kwargs):
    try:
        company = Company.objects.get(pk=instance.pk)
        if company.logo and company.logo != instance.logo and os.path.isfile(company.logo.path):
            os.remove(company.logo.path)
    except Exception as e:
        print(e)


@receiver(post_delete, sender=Company)
def delete_logo(instance, *args, **kwargs):
    if instance.logo and os.path.isfile(instance.logo.path):
        os.remove(instance.logo.path)

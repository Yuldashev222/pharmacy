from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from api.v1.apps.accounts.models import WorkerReport

from .models import PharmacyIncome, PharmacyIncomeReportDay


@receiver(post_delete, sender=PharmacyIncome)
def update_user_income_report(instance, *args, **kwargs):
    price = PharmacyIncome.objects.filter(
        report_date=instance.report_date,
        to_pharmacy_id=instance.to_pharmacy_id
    ).aggregate(s=Sum('price'))['s']
    obj = PharmacyIncomeReportDay.objects.get_or_create(
        pharmacy_id=instance.to_pharmacy_id,
        report_date=instance.report_date,
        director_id=instance.creator.director_id
    )[0]
    obj.price = price if price else 0
    print(price)
    obj.save()


@receiver(post_save, sender=PharmacyIncome)
def update_report(instance, *args, **kwargs):
    if instance.to_user:
        obj, _ = WorkerReport.objects.get_or_create(pharmacy_income_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = instance.price
        obj.creator_id = instance.creator_id
        obj.worker_id = instance.to_user_id
        obj.created_at = instance.created_at
        obj.is_expense = False
        obj.save()
    else:
        WorkerReport.objects.filter(pharmacy_income_id=instance.id).delete()

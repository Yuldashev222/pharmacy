import os

from django.db.models import Sum
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from api.v1.apps.companies.models import Company

from .models import CustomUser, WorkerReport, WorkerReportMonth


@receiver(post_save, sender=CustomUser)
def create_company(instance, created, *args, **kwargs):
    if created:
        if instance.is_director:
            Company.objects.create(
                name=f'Company::{instance.first_name}-{instance.last_name}',
                director_id=instance.id
            )
            instance.director_id = instance.id
            instance.save()


@receiver(post_delete, sender=CustomUser)
def delete_photo(instance, *args, **kwargs):
    # old_photo = CustomUser.objects.get(pk=obj.pk).logo
    if instance.photo and os.path.isfile(instance.photo.path):
        os.remove(instance.photo.path)  # last


@receiver(pre_save, sender=WorkerReport)
def update_user_month_report(instance, *args, **kwargs):
    if not instance.pk:
        old_worker = WorkerReport.objects.filter(id=instance.id)
        if old_worker.exists() and instance.worker and instance.worker != old_worker:
            old_worker = old_worker.first().worker
            obj, _ = WorkerReportMonth.objects.get_or_create(
                month=instance.report_date.month, year=instance.report_date.year, worker_id=old_worker.id)

            expense_price, income_price = (
                WorkerReport.objects.filter(
                    is_expense=True, report_date__year=obj.year, report_date__month=obj.month, worker_id=obj.worker_id
                ).aggregate(s=Sum('price'))['s'],
                WorkerReport.objects.filter(
                    is_expense=False, report_date__year=obj.year, report_date__month=obj.month, worker_id=obj.worker_id
                ).aggregate(s=Sum('price'))['s']
            )
            obj.expense_price = expense_price if expense_price else 0
            obj.income_price = income_price if income_price else 0
            obj.save()


@receiver(post_save, sender=WorkerReport)
def update_report(instance, *args, **kwargs):
    if instance.report_date and instance.worker:
        obj, _ = WorkerReportMonth.objects.get_or_create(
            month=instance.report_date.month, year=instance.report_date.year, worker_id=instance.worker_id)

        expense_price, income_price = (
            WorkerReport.objects.filter(
                is_expense=True, report_date__year=obj.year, report_date__month=obj.month, worker_id=obj.worker_id
            ).aggregate(s=Sum('price'))['s'],
            WorkerReport.objects.filter(
                is_expense=False, report_date__year=obj.year, report_date__month=obj.month, worker_id=obj.worker_id
            ).aggregate(s=Sum('price'))['s']
        )
        obj.expense_price = expense_price if expense_price else 0
        obj.income_price = income_price if income_price else 0
        obj.save()

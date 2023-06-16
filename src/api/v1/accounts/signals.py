import os
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from .models import CustomUser, WorkerReport, WorkerReportMonth
from ..companies.models import Company


@receiver(post_save, sender=CustomUser)
def create_company(instance, created, *args, **kwargs):
    if created and instance.is_director:
        instance.director_id = instance.id
        instance.save()
        Company.objects.create(name=str(instance), director_id=instance.id)

    try:
        user = CustomUser.objects.get(pk=instance.pk)
        if user.photo and user.photo != instance.photo and os.path.isfile(user.photo.path):
            os.remove(user.photo.path)
    except Exception as e:
        print(e)


@receiver(post_delete, sender=CustomUser)
def delete_photo(instance, *args, **kwargs):
    if instance.photo and os.path.isfile(instance.photo.path):
        os.remove(instance.photo.path)


@receiver(pre_save, sender=WorkerReport)
def update_user_month_report(instance, *args, **kwargs):
    if instance.pk and instance.worker and instance.report_date:
        old_worker = WorkerReport.objects.get(id=instance.id).worker
        if old_worker and instance.worker_id != old_worker.id:
            obj, _ = WorkerReportMonth.objects.get_or_create(month=instance.report_date.month,
                                                             year=instance.report_date.year,
                                                             worker=old_worker,
                                                             pharmacy=instance.pharmacy)

            expense_price = WorkerReport.objects.filter(is_expense=True,
                                                        report_date__year=obj.year,
                                                        report_date__month=obj.month,
                                                        worker=obj.worker,
                                                        pharmacy=obj.pharmacy
                                                        ).aggregate(s=Sum('price'))['s']

            income_price = WorkerReport.objects.filter(is_expense=False,
                                                       report_date__year=obj.year,
                                                       report_date__month=obj.month,
                                                       worker_id=obj.worker_id,
                                                       pharmacy=obj.pharmacy
                                                       ).aggregate(s=Sum('price'))['s']

            obj.expense_price = expense_price if expense_price else 0
            obj.income_price = income_price if income_price else 0
            obj.save()


@receiver(post_save, sender=WorkerReport)
def update_report(instance, *args, **kwargs):
    if instance.report_date and instance.worker:
        obj, _ = WorkerReportMonth.objects.get_or_create(month=instance.report_date.month,
                                                         year=instance.report_date.year,
                                                         worker=instance.worker,
                                                         pharmacy=instance.pharmacy)

        expense_price = WorkerReport.objects.filter(is_expense=True,
                                                    report_date__year=obj.year,
                                                    report_date__month=obj.month,
                                                    worker=obj.worker,
                                                    pharmacy=obj.pharmacy
                                                    ).aggregate(s=Sum('price'))['s']

        income_price = WorkerReport.objects.filter(is_expense=False,
                                                   report_date__year=obj.year,
                                                   report_date__month=obj.month,
                                                   worker=obj.worker,
                                                   pharmacy=obj.pharmacy
                                                   ).aggregate(s=Sum('price'))['s']

        obj.expense_price = expense_price if expense_price else 0
        obj.income_price = income_price if income_price else 0
        obj.save()
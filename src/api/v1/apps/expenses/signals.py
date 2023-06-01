from django.dispatch import receiver
from django.db.models import Sum
from django.db.models.signals import post_delete, post_save

from api.v1.apps.accounts.models import WorkerReport
from api.v1.apps.remainders.models import Remainder

from .models import PharmacyExpense, UserExpense
from .reports.models import ExpenseReportMonth


@receiver(post_save, sender=PharmacyExpense)
def update_report(instance, *args, **kwargs):
    # remainder update
    if instance.transfer_type_id == 1:
        obj, _ = Remainder.objects.get_or_create(pharmacy_expense_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = -1 * instance.price
        obj.shift = instance.shift
        obj.pharmacy_id = instance.from_pharmacy_id
        obj.save()


@receiver(post_delete, sender=PharmacyExpense)
def update_report(instance, *args, **kwargs):
    price = PharmacyExpense.objects.filter(
        from_pharmacy_id=instance.from_pharmacy_id,
        expense_type_id=instance.expense_type_id,
        report_date__year=instance.report_date.year,
        report_date__month=instance.report_date.month
    ).aggregate(s=Sum('price'))['s']
    obj, _ = ExpenseReportMonth.objects.get_or_create(
        pharmacy_id=instance.from_pharmacy_id,
        expense_type_id=instance.expense_type_id,
        year=instance.report_date.year,
        month=instance.report_date.month
    )
    obj.price = price if price else 0
    obj.save()


@receiver(post_save, sender=UserExpense)
def update_user_expense_report(instance, *args, **kwargs):
    # remainder update
    if instance.transfer_type_id == 1 and instance.to_pharmacy:
        obj, _ = Remainder.objects.get_or_create(user_expense_id=instance.id)
        obj.is_expense = False
        obj.report_date = instance.report_date
        obj.price = instance.price
        obj.shift = instance.shift
        obj.pharmacy_id = instance.to_pharmacy_id
        obj.save()

    # worker reports update
    obj, _ = WorkerReport.objects.get_or_create(user_expense_id=instance.id, is_expense=True)
    obj.report_date = instance.report_date
    obj.price = instance.price
    obj.creator_id = instance.creator_id
    obj.pharmacy = instance.to_pharmacy
    obj.worker_id = instance.from_user_id
    obj.created_at = instance.created_at
    obj.save()

    if instance.to_user:
        obj, _ = WorkerReport.objects.get_or_create(user_expense_id=instance.id, is_expense=False)
        obj.report_date = instance.report_date
        obj.price = instance.price
        obj.creator_id = instance.creator_id
        obj.pharmacy = instance.to_pharmacy
        obj.worker_id = instance.to_user_id
        obj.created_at = instance.created_at
        obj.is_expense = False
        obj.save()
    else:
        WorkerReport.objects.filter(user_expense_id=instance.id, is_expense=False).delete()

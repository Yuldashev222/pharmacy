from django.dispatch import receiver
from django.db.models import Sum, Q
from django.db.models.signals import pre_delete, post_save

from api.v1.accounts.models import WorkerReport
from api.v1.companies.enums import DefaultTransferType
from api.v1.remainders.models import RemainderDetail
from api.v1.pharmacies.models import PharmacyReportByShift

from .enums import DefaultExpenseType
from .models import PharmacyExpense, UserExpense
from .reports.models import ExpenseReportMonth


@receiver(post_save, sender=PharmacyExpense)
def update_report(instance, *args, **kwargs):
    # remainder update
    if instance.transfer_type_id == DefaultTransferType.cash.value:
        obj, _ = RemainderDetail.objects.get_or_create(pharmacy_expense_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = -1 * instance.price
        obj.shift = instance.shift
        obj.pharmacy_id = instance.from_pharmacy_id
        obj.save()

        obj, _ = PharmacyReportByShift.objects.get_or_create(pharmacy_id=instance.from_pharmacy_id,
                                                             report_date=instance.report_date,
                                                             shift=instance.shift)

        if instance.expense_type_id != DefaultExpenseType.discount_id.value:

            expense_pharmacy = PharmacyExpense.objects.exclude(expense_type_id=DefaultExpenseType.discount_id.value
                                                               ).filter(from_pharmacy_id=obj.pharmacy_id,
                                                                        report_date=obj.report_date,
                                                                        shift=obj.shift,
                                                                        transfer_type_id=DefaultTransferType.cash.value
                                                                        ).aggregate(s=Sum('price'))['s']

            obj.expense_pharmacy = expense_pharmacy if expense_pharmacy else 0

        else:
            not_transfer_discount_price = PharmacyExpense.objects.filter(from_pharmacy_id=obj.pharmacy_id,
                                                                         report_date=obj.report_date,
                                                                         shift=obj.shift,
                                                                         transfer_type_id=DefaultTransferType.cash.value,
                                                                         expense_type_id=DefaultExpenseType.discount_id.value,
                                                                         ).aggregate(s=Sum('price'))['s']

            obj.not_transfer_discount_price = not_transfer_discount_price if not_transfer_discount_price else 0

        obj.save()

    elif instance.expense_type_id == DefaultExpenseType.discount_id.value:
        obj, _ = PharmacyReportByShift.objects.get_or_create(pharmacy_id=instance.from_pharmacy_id,
                                                             report_date=instance.report_date,
                                                             shift=instance.shift)

        transfer_discount_price = PharmacyExpense.objects.exclude(transfer_type_id=DefaultTransferType.cash.value
                                               ).filter(from_pharmacy_id=obj.pharmacy_id,
                                                        report_date=obj.report_date,
                                                        shift=obj.shift,
                                                        expense_type_id=DefaultExpenseType.discount_id.value,
                                                        ).aggregate(s=Sum('price'))['s']

        obj.transfer_discount_price = transfer_discount_price if transfer_discount_price else 0
        obj.save()

    if instance.to_user:
        obj, _ = WorkerReport.objects.get_or_create(pharmacy_expense_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = instance.price
        obj.creator = instance.creator
        obj.pharmacy_id = instance.from_pharmacy.id
        obj.worker_id = instance.to_user.id
        obj.created_at = instance.created_at
        obj.is_expense = False
        obj.save()
    else:
        WorkerReport.objects.filter(pharmacy_expense_id=instance.id).delete()


@receiver(pre_delete, sender=PharmacyExpense)
def update_report(instance, *args, **kwargs):
    obj, _ = ExpenseReportMonth.objects.get_or_create(pharmacy_id=instance.from_pharmacy_id,
                                                      expense_type_id=instance.expense_type_id,
                                                      year=instance.report_date.year,
                                                      month=instance.report_date.month)

    price = PharmacyExpense.objects.exclude(id=instance.id).filter(from_pharmacy_id=obj.pharmacy_id,
                                                                   expense_type_id=obj.expense_type_id,
                                                                   report_date__year=obj.year,
                                                                   report_date__month=obj.month
                                                                   ).aggregate(s=Sum('price'))['s']

    obj.price = price if price else 0
    obj.save()

    if instance.transfer_type_id == DefaultTransferType.cash.value:
        obj, _ = PharmacyReportByShift.objects.get_or_create(pharmacy_id=instance.from_pharmacy_id,
                                                             report_date=instance.report_date,
                                                             shift=instance.shift)

        if instance.expense_type_id != DefaultExpenseType.discount_id.value:
            expense_pharmacy = PharmacyExpense.objects.exclude(Q(id=instance.id) |
                                                               Q(expense_type_id=DefaultExpenseType.discount_id.value)
                                                               ).filter(from_pharmacy_id=obj.pharmacy_id,
                                                                        report_date=obj.report_date,
                                                                        transfer_type_id=DefaultTransferType.cash.value,
                                                                        shift=obj.shift
                                                                        ).aggregate(s=Sum('price'))['s']

            obj.expense_pharmacy = expense_pharmacy if expense_pharmacy else 0

        else:
            objs = PharmacyExpense.objects.exclude(id=instance.id).filter(from_pharmacy_id=obj.pharmacy_id,
                                                                          report_date=obj.report_date,
                                                                          shift=obj.shift,
                                                                          transfer_type_id=DefaultTransferType.cash.value,
                                                                          expense_type_id=DefaultExpenseType.discount_id.value
                                                                          ).values_list('price', flat=True)

            not_transfer_discount_price = sum(list(map(lambda x: int(x) if str(x).isdigit() else 0, objs)))
            obj.not_transfer_discount_price = not_transfer_discount_price

        obj.save()

    elif instance.expense_type_id == DefaultExpenseType.discount_id.value:
        obj, _ = PharmacyReportByShift.objects.get_or_create(pharmacy_id=instance.from_pharmacy_id,
                                                             report_date=instance.report_date,
                                                             shift=instance.shift)

        objs = PharmacyExpense.objects.exclude(id=instance.id
                                               ).exclude(transfer_type_id=DefaultTransferType.cash.value
                                                         ).filter(from_pharmacy_id=obj.pharmacy_id,
                                                                  report_date=obj.report_date,
                                                                  shift=obj.shift,
                                                                  expense_type_id=DefaultExpenseType.discount_id.value
                                                                  ).values_list('price', flat=True)

        transfer_discount_price = sum(list(map(lambda x: int(x) if str(x).isdigit() else 0, objs)))
        obj.transfer_discount_price = transfer_discount_price
        obj.save()


@receiver(post_save, sender=UserExpense)
def update_user_expense_report(instance, *args, **kwargs):
    # worker reports update
    obj, _ = WorkerReport.objects.get_or_create(user_expense_id=instance.id, is_expense=True)
    obj.report_date = instance.report_date
    obj.price = instance.price
    obj.creator = instance.creator
    obj.pharmacy = instance.to_pharmacy
    obj.worker_id = instance.from_user.id
    obj.created_at = instance.created_at
    obj.save()

    if instance.to_user:
        obj, _ = WorkerReport.objects.get_or_create(user_expense_id=instance.id, is_expense=False)
        obj.report_date = instance.report_date
        obj.price = instance.price
        obj.creator = instance.creator
        obj.pharmacy = instance.to_pharmacy
        obj.worker_id = instance.to_user.id
        obj.created_at = instance.created_at
        obj.is_expense = False
        obj.save()
    else:
        WorkerReport.objects.filter(user_expense_id=instance.id, is_expense=False).delete()

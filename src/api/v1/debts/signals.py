from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from api.v1.accounts.models import WorkerReport
from api.v1.companies.enums import DefaultTransferType
from api.v1.remainders.models import RemainderDetail
from api.v1.pharmacies.models import PharmacyReportByShift

from .models import DebtRepayFromPharmacy, DebtFromPharmacy, DebtRepayToPharmacy, DebtToPharmacy


@receiver(post_save, sender=DebtFromPharmacy)
def report_update(instance, *args, **kwargs):
    obj, _ = PharmacyReportByShift.objects.get_or_create(pharmacy_id=instance.from_pharmacy_id,
                                                         report_date=instance.report_date,
                                                         shift=instance.shift)

    # remainder update
    if instance.transfer_type_id == DefaultTransferType.cash.value and not instance.is_client:  # last
        obj, _ = RemainderDetail.objects.get_or_create(debt_from_pharmacy_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = -1 * instance.price
        obj.shift = instance.shift
        obj.pharmacy_id = instance.from_pharmacy_id
        obj.save()

        expense_debt_from_pharmacy = DebtFromPharmacy.objects.filter(from_pharmacy_id=obj.pharmacy_id,
                                                                     report_date=obj.report_date,
                                                                     shift=obj.shift,
                                                                     is_client=False,
                                                                     transfer_type_id=DefaultTransferType.cash.value
                                                                     ).aggregate(s=Sum('price'))['s']

        obj.expense_debt_from_pharmacy = expense_debt_from_pharmacy if expense_debt_from_pharmacy else 0
        obj.save()

    debt_income = DebtFromPharmacy.objects.filter(from_pharmacy_id=obj.pharmacy_id,
                                                  report_date=obj.report_date,
                                                  shift=obj.shift,
                                                  is_client=True,
                                                  ).aggregate(s=Sum('price'))['s']

    obj.debt_income = debt_income if debt_income else 0
    obj.save()


@receiver(post_save, sender=DebtRepayToPharmacy)
def report_update(instance, *args, **kwargs):
    # remainder update
    if instance.transfer_type_id == DefaultTransferType.cash.value:
        obj, _ = RemainderDetail.objects.get_or_create(debt_repay_to_pharmacy_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = instance.price
        obj.shift = instance.shift
        obj.pharmacy_id = instance.from_debt.from_pharmacy_id
        obj.save()


@receiver(post_save, sender=DebtRepayFromPharmacy)
def report_update(instance, *args, **kwargs):
    # remainder update
    if instance.transfer_type_id == DefaultTransferType.cash.value and not instance.from_user:
        obj, _ = RemainderDetail.objects.get_or_create(debt_repay_from_pharmacy_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = -1 * instance.price
        obj.shift = instance.shift
        obj.pharmacy_id = instance.to_debt.to_pharmacy_id
        obj.save()

        obj, _ = PharmacyReportByShift.objects.get_or_create(pharmacy_id=instance.to_debt.to_pharmacy_id,
                                                             report_date=instance.report_date,
                                                             shift=instance.shift)

        expense_debt_repay_from_pharmacy = DebtRepayFromPharmacy.objects.filter(to_debt__to_pharmacy_id=obj.pharmacy_id,
                                                                                report_date=obj.report_date,
                                                                                shift=obj.shift,
                                                                                from_user__isnull=True,
                                                                                transfer_type_id=DefaultTransferType.cash.value
                                                                                ).aggregate(s=Sum('price'))['s']

        obj.expense_debt_repay_from_pharmacy = expense_debt_repay_from_pharmacy if expense_debt_repay_from_pharmacy else 0
        obj.save()

    # worker reports update
    if instance.from_user:
        obj, _ = WorkerReport.objects.get_or_create(debt_repay_from_pharmacy_id=instance.id)
        obj.report_date = instance.report_date
        obj.pharmacy = instance.to_debt.to_pharmacy
        obj.price = instance.price
        obj.creator_id = instance.creator_id
        obj.worker = instance.from_user
        obj.created_at = instance.created_at
        obj.save()
    else:
        WorkerReport.objects.filter(debt_repay_from_pharmacy_id=instance.id).delete()


@receiver(post_save, sender=DebtToPharmacy)
def remainder_update(instance, *args, **kwargs):
    try:
        obj = instance.to_firm_expense or instance.pharmacy_expense or instance.user_expense
        if obj and obj.transfer_type_id == DefaultTransferType.cash.value:
            obj, _ = RemainderDetail.objects.get_or_create(debt_to_pharmacy_id=instance.id)
            obj.report_date = instance.report_date
            obj.price = instance.price
            obj.shift = instance.shift
            obj.pharmacy_id = instance.to_pharmacy_id
            obj.save()
    except Exception as e:
        print(e)


@receiver(post_delete, sender=DebtToPharmacy)
def remainder_update(instance, *args, **kwargs):
    obj = instance.to_firm_expense or instance.pharmacy_expense or instance.user_expense
    if obj:
        obj.save()

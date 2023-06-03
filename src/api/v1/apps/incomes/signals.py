from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from api.v1.apps.accounts.models import WorkerReport
from api.v1.apps.companies.enums import DefaultTransferType
from api.v1.apps.remainders.models import RemainderDetail
from api.v1.apps.pharmacies.models import PharmacyReportByShift

from .models import PharmacyIncome, PharmacyIncomeReportDay


@receiver(post_delete, sender=PharmacyIncome)
def update_user_income_report(instance, *args, **kwargs):
    price = PharmacyIncome.objects.filter(report_date=instance.report_date, to_pharmacy_id=instance.to_pharmacy_id
                                          ).aggregate(s=Sum('price'))['s']
    obj = PharmacyIncomeReportDay.objects.get_or_create(
        pharmacy_id=instance.to_pharmacy_id, report_date=instance.report_date)[0]
    obj.price = price if price else 0
    print(price)
    obj.save()


@receiver(post_save, sender=PharmacyIncome)
def update_report(instance, *args, **kwargs):
    obj, _ = PharmacyReportByShift.objects.get_or_create(pharmacy_id=instance.to_pharmacy_id,
                                                         report_date=instance.report_date,
                                                         shift=instance.shift)

    if instance.transfer_type_id == DefaultTransferType.cash.value:

        transfer_income = PharmacyIncome.objects.exclude(transfer_type_id=DefaultTransferType.cash.value
                                                         ).filter(report_date=obj.report_date,
                                                                  to_pharmacy_id=obj.pharmacy_id,
                                                                  shift=obj.shift).aggregate(s=Sum('price'))['s']
        obj.transfer_income = transfer_income if transfer_income else 0
    else:
        not_transfer_income = PharmacyIncome.objects.filter(report_date=obj.report_date,
                                                            to_pharmacy_id=obj.pharmacy_id,
                                                            shift=obj.shift,
                                                            transfer_type_id=DefaultTransferType.cash.value
                                                            ).aggregate(s=Sum('price'))['s']
        obj.not_transfer_income = not_transfer_income if not_transfer_income else 0
    obj.save()

    # remainder update
    if instance.transfer_type_id == DefaultTransferType.cash.value and not instance.to_user:
        obj, _ = RemainderDetail.objects.get_or_create(pharmacy_income_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = instance.price
        obj.shift = instance.shift
        obj.pharmacy_id = instance.to_pharmacy_id
        obj.save()

    if instance.to_user:
        obj, _ = WorkerReport.objects.get_or_create(pharmacy_income_id=instance.id)
        obj.report_date = instance.report_date
        obj.pharmacy = instance.to_pharmacy
        obj.price = instance.price
        obj.creator_id = instance.creator_id
        obj.worker_id = instance.to_user_id
        obj.created_at = instance.created_at
        obj.is_expense = False
        obj.save()
    else:
        WorkerReport.objects.filter(pharmacy_income_id=instance.id).delete()

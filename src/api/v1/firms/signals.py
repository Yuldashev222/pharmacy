from django.dispatch import receiver
from django.db.models import Sum
from django.db.models.signals import post_save, pre_delete

from api.v1.accounts.models import WorkerReport
from api.v1.companies.enums import DefaultTransferType
from api.v1.remainders.models import RemainderDetail
from api.v1.pharmacies.models import PharmacyReportByShift

from .models import FirmIncome, FirmExpense, FirmReport, FirmDebtByMonth, FirmExcessExpense


@receiver(post_save, sender=FirmIncome)
def update_excess_price(instance, created, *args, **kwargs):
    if created:
        objs = FirmExcessExpense.objects.filter(firm_id=instance.from_firm_id,
                                                is_transfer=instance.is_transfer_return,
                                                remaining_price__gt=0).order_by('report_date', 'id')
        for obj in objs:
            if instance.remaining_debt <= 0:
                break
            if instance.remaining_debt <= obj.remaining_price:
                obj.remaining_price -= instance.remaining_debt
                instance.remaining_debt = 0
                instance.is_paid = True
            else:
                instance.remaining_debt -= obj.remaining_price
                obj.remaining_price = 0
            obj.firm_income_id = instance.id
            obj.save()


@receiver(pre_delete, sender=FirmReport)
def update_firm_report(instance, *args, **kwargs):
    if instance.firm and instance.report_date:
        not_transfer_debt = FirmReport.objects.exclude(id=instance.id).filter(firm_id=instance.firm_id,
                                                                              is_transfer=False,
                                                                              ).aggregate(s=Sum('price'))['s']

        transfer_debt = FirmReport.objects.exclude(id=instance.id).filter(firm_id=instance.firm_id,
                                                                          is_transfer=True,
                                                                          ).aggregate(s=Sum('price'))['s']

        instance.firm.transfer_debt = transfer_debt
        instance.firm.not_transfer_debt = not_transfer_debt
        instance.firm.save()

    if instance.pharmacy:
        by_month, _ = FirmDebtByMonth.objects.get_or_create(month=instance.report_date.month,
                                                            year=instance.report_date.year,
                                                            firm_id=instance.firm_id,
                                                            pharmacy=instance.pharmacy)

        expense_price = FirmReport.objects.exclude(id=instance.id).filter(report_date__year=by_month.year,
                                                                          report_date__month=by_month.month,
                                                                          firm_id=by_month.firm_id,
                                                                          pharmacy=by_month.pharmacy,
                                                                          is_expense=True
                                                                          ).aggregate(s=Sum('price'))['s']

        by_month.expense_price = expense_price if expense_price else 0
        by_month.save()


@receiver(post_save, sender=FirmExpense)
def report_update(instance, *args, **kwargs):
    if instance.is_verified:
        print(11111111111111111)
        # remainder update
        if instance.transfer_type_id == DefaultTransferType.cash.value and not instance.from_user:
            obj, _ = RemainderDetail.objects.get_or_create(firm_expense_id=instance.id)
            obj.report_date = instance.report_date
            obj.price = -1 * instance.price
            obj.shift = instance.shift
            obj.pharmacy_id = instance.from_pharmacy_id
            obj.save()

            obj, _ = PharmacyReportByShift.objects.get_or_create(pharmacy_id=instance.from_pharmacy_id,
                                                                 report_date=instance.report_date,
                                                                 shift=instance.shift)

            expense_firm = FirmExpense.objects.filter(from_pharmacy_id=obj.pharmacy_id,
                                                      is_verified=True,
                                                      from_user__isnull=True,
                                                      transfer_type_id=DefaultTransferType.cash.value,
                                                      report_date=obj.report_date,
                                                      shift=obj.shift
                                                      ).aggregate(s=Sum('price'))['s']

            obj.expense_firm = expense_firm if expense_firm else 0
            obj.save()

        if instance.from_user:
            obj, _ = WorkerReport.objects.get_or_create(firm_expense_id=instance.id)
            obj.report_date = instance.report_date
            obj.pharmacy = instance.from_pharmacy
            obj.price = instance.price
            obj.creator_id = instance.creator_id
            obj.worker = instance.from_user
            obj.created_at = instance.created_at
            obj.save()
        else:
            WorkerReport.objects.filter(firm_expense_id=instance.id).delete()

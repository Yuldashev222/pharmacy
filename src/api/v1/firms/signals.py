from django.dispatch import receiver
from django.db.models import Sum
from django.db.models.signals import post_save, pre_delete

from api.v1.accounts.models import WorkerReport
from api.v1.companies.enums import DefaultTransferType
from api.v1.remainders.models import RemainderDetail
from api.v1.pharmacies.models import PharmacyReportByShift

from .models import FirmIncome, FirmExpense, FirmReport, FirmDebtByDate, FirmDebtByMonth


@receiver(pre_delete, sender=FirmReport)
def update_firm_report(instance, *args, **kwargs):
    firm_debt, _ = FirmDebtByDate.objects.get_or_create(firm_id=instance.firm_id, report_date=instance.report_date)
    objs = FirmIncome.objects.filter(is_paid=False,
                                     is_transfer_return=False,
                                     from_firm_id=firm_debt.firm_id,
                                     report_date__lte=firm_debt.report_date)

    objs2 = FirmIncome.objects.filter(is_paid=False,
                                      is_transfer_return=True,
                                      from_firm_id=firm_debt.firm_id,
                                      report_date__lte=firm_debt.report_date)

    if instance.income:
        objs = objs.exclude(id=instance.income.id)
        objs2 = objs2.exclude(id=instance.income.id)

    incomes_not_transfer_debt_price = objs.aggregate(s=Sum('remaining_debt'))['s']
    incomes_transfer_debt_price = objs2.aggregate(s=Sum('remaining_debt'))['s']

    incomes_not_transfer_debt_price = incomes_not_transfer_debt_price if incomes_not_transfer_debt_price else 0
    incomes_transfer_debt_price = incomes_transfer_debt_price if incomes_transfer_debt_price else 0

    firm_debt.incomes_not_transfer_debt_price = incomes_not_transfer_debt_price
    firm_debt.incomes_transfer_debt_price = incomes_transfer_debt_price
    firm_debt.save()

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

    income_price = FirmReport.objects.exclude(id=instance.id).filter(report_date__year=by_month.year,
                                                                     report_date__month=by_month.month,
                                                                     firm_id=by_month.firm_id,
                                                                     pharmacy=by_month.pharmacy,
                                                                     is_expense=False
                                                                     ).aggregate(s=Sum('price'))['s']

    by_month.expense_price = expense_price if expense_price else 0
    by_month.income_price = income_price if income_price else 0
    by_month.save()


@receiver(post_save, sender=FirmExpense)
def report_update(instance, *args, **kwargs):
    if instance.is_verified:

        # remainder update
        if instance.transfer_type_id == DefaultTransferType.cash.value and not instance.from_user:  # last
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

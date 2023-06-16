# from django.dispatch import receiver
# from django.db import transaction
# from django.db.models.signals import pre_delete
#
# from api.v1.accounts.models import CustomUser, WorkerReport, WorkerReportMonth
# from api.v1.debts.models import DebtToPharmacy, DebtFromPharmacy
# from api.v1.expenses.models import UserExpense, PharmacyExpense
# from api.v1.firms.models import FirmExpense
#
# from .models import Pharmacy
#
#
# @transaction.atomic
# @receiver(pre_delete, sender=Pharmacy)
# def update_connections(instance, *args, **kwargs):
#     WorkerReportMonth.objects.filter(pharmacy_id=instance.id).delete()
#     WorkerReport.objects.filter(pharmacy_id=instance.id).delete()
#     CustomUser.objects.filter(pharmacy_id=instance.id).delete()
#     DebtToPharmacy.objects.filter(to_pharmacy_id=instance.id).delete()
#     DebtFromPharmacy.objects.filter(from_pharmacy_id=instance.id).delete()
#     UserExpense.objects.filter(to_pharmacy_id=instance.id).delete()
#     PharmacyExpense.objects.filter(from_pharmacy_id=instance.id).delete()
#     FirmExpense.objects.filter(from_pharmacy_id=instance.id).delete()
#     FirmExpense.objects.filter(from_pharmacy_id=instance.id).delete()

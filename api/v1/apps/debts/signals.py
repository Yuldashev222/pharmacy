# from django.db.models.signals import pre_save
# from django.dispatch import receiver
#
# from .models import DebtRepayFromPharmacy
#
#
# @receiver(pre_save, sender=DebtRepayFromPharmacy)
# def change_remaining_debt(instance, *args, **kwargs):
#     old_price = DebtToPharmacy.objects.get(pk=instance.pk).price
#     if old_price != instance.price:
#         instance.remaining_debt += instance.price - instance.remaining_debt
#     # if instance.photo and os.path.isfile(instance.photo.path):
#     #     os.remove(instance.photo.path)  # last

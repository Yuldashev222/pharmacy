from datetime import timedelta, datetime, time, date
from django.conf import settings
from django.contrib.auth.hashers import make_password

from api.v1.accounts.models import CustomUser

from . import models


def get_deleted_pharmacy_obj(obj):
    password = make_password(settings.FAKE_DIRECTOR_DEFAULT_PASSWORD)
    obj, _ = models.Pharmacy.objects.get_or_create(name=f'deleted {obj.name[:90]}',
                                                   password=password,
                                                   director_id=CustomUser.get_fake_director())
    return obj


def pharmacy_logo_upload_location(obj, logo):
    return f'pharmacies/{obj.name[:200]}/logos/{logo}'


def get_worker_report_date(pharmacy_hour):
    now_time = datetime.now().time()
    today_date = date.today()
    if now_time > time(hour=pharmacy_hour):
        return today_date
    return today_date - timedelta(days=1)

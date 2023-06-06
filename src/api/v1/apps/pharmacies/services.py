from datetime import timedelta, datetime, time, date


def pharmacy_logo_upload_location(obj, logo):
    return f'pharmacies/{obj.name[:200]}/logos/{logo}'


def get_worker_report_date(pharmacy_hour):
    now_time = datetime.now().time()
    today_date = date.today()
    if now_time > time(hour=pharmacy_hour):
        return today_date
    return today_date - timedelta(days=1)

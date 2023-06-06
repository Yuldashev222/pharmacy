from rest_framework import permissions

from api.v1.apps.pharmacies.services import get_worker_report_date


class WorkerTodayObject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        worker = request.user
        report_date = get_worker_report_date(worker.pharmacy.last_shift_end_hour)
        return worker.shift == obj.shift and obj.report_date == report_date

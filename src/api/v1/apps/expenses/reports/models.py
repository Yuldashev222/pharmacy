from django.db import models

from api.v1.apps.companies.reports.models import AllReturnProductReportMonth


class ReturnProductReportMonth(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    year = models.IntegerField()
    month = models.IntegerField()
    price = models.IntegerField(default=0)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        price = ReturnProductReportMonth.objects.filter(month=self.month).aggregate(s=models.Sum('price'))['s']
        obj = AllReturnProductReportMonth.objects.get_or_create(
            year=self.year,
            month=self.month,
            director_id=self.director_id
        )[0]
        obj.price = price if price else 0
        obj.save()

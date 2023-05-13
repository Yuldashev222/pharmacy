# Generated by Django 4.2 on 2023-05-13 08:20

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reports', '0001_initial'),
        ('pharmacies', '0001_initial'),
        ('general', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PharmacyIncome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('price', models.PositiveIntegerField()),
                ('shift', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(3), django.core.validators.MinValueValidator(1)])),
                ('desc', models.CharField(blank=True, max_length=500)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.report')),
                ('to_pharmacy', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pharmacies.pharmacy')),
                ('to_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='pharmacy_incomes', to=settings.AUTH_USER_MODEL)),
                ('transfer_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='general.transfermoneytype')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
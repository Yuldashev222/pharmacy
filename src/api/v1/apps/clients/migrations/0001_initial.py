# Generated by Django 4.2 on 2023-05-13 08:20

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number1', models.CharField(max_length=13, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_phone_number', message='Phone number must be entered in the format: "+998976543210". Up to 13 digits allowed.', regex='^[+]998\\d{9}$')])),
                ('phone_number2', models.CharField(blank=True, max_length=13, validators=[django.core.validators.RegexValidator(code='invalid_phone_number', message='Phone number must be entered in the format: "+998976543210". Up to 13 digits allowed.', regex='^[+]998\\d{9}$')])),
                ('first_name', models.CharField(max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('total_amount', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('bio', models.CharField(blank=True, max_length=500)),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=500)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('director', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='clients', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
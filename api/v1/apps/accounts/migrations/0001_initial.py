# Generated by Django 4.2 on 2023-04-27 11:19

import api.v1.apps.accounts.managers
import api.v1.apps.accounts.services
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone_number', models.CharField(max_length=13, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_phone_number', message='Phone number must be entered in the format: "+998976543210". Up to 13 digits allowed.', regex='^[+]998\\d{9}$')])),
                ('role', models.CharField(choices=[('p', 'Project Owner'), ('d', 'Director'), ('m', 'Manager'), ('w', 'Worker')], max_length=1)),
                ('shift', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(3)])),
                ('start_date_for_wage', models.DateField(blank=True, null=True)),
                ('wage', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('bio', models.CharField(blank=True, max_length=500)),
                ('photo', models.ImageField(blank=True, null=True, upload_to=api.v1.apps.accounts.services.user_photo_upload_location)),
                ('address', models.CharField(blank=True, max_length=500)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', api.v1.apps.accounts.managers.CustomUserManager()),
            ],
        ),
    ]

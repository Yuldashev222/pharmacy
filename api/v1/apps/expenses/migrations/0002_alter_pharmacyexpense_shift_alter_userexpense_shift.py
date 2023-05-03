# Generated by Django 4.2 on 2023-05-03 07:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pharmacyexpense',
            name='shift',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(3), django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='userexpense',
            name='shift',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(3), django.core.validators.MinValueValidator(1)]),
        ),
    ]

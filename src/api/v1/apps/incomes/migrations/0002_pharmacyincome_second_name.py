# Generated by Django 4.2 on 2023-05-13 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incomes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pharmacyincome',
            name='second_name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]

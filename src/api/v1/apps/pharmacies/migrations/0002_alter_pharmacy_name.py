# Generated by Django 4.2 on 2023-05-12 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pharmacy',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]

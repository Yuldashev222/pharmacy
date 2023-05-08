# Generated by Django 4.2 on 2023-05-08 18:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferMoneyType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='companies.company')),
            ],
            options={
                'unique_together': {('name', 'company')},
            },
        ),
        migrations.CreateModel(
            name='ExpenseType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('desc', models.CharField(blank=True, max_length=600)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='companies.company')),
            ],
            options={
                'unique_together': {('name', 'company')},
            },
        ),
    ]

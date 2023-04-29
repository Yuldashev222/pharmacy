# Generated by Django 4.2 on 2023-04-29 11:23

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pharmacies', '0001_initial'),
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DebtIncome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('shift', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(3)])),
                ('is_paid', models.BooleanField(default=False)),
                ('desc', models.CharField(max_length=500)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.report')),
                ('to_pharmacy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='pharmacies.pharmacy')),
                ('to_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='debt_incomes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DebtExpense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('shift', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(3)])),
                ('desc', models.CharField(blank=True, max_length=500)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('from_pharmacy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='pharmacies.pharmacy')),
                ('from_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='debt_expenses', to=settings.AUTH_USER_MODEL)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.report')),
                ('to_debt', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='debts.debtincome')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

# Generated by Django 4.2 on 2023-05-08 19:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('general', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='expensetype',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='transfermoneytype',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='expensetype',
            name='director',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transfermoneytype',
            name='director',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='expensetype',
            unique_together={('name', 'director')},
        ),
        migrations.AlterUniqueTogether(
            name='transfermoneytype',
            unique_together={('name', 'director')},
        ),
        migrations.RemoveField(
            model_name='expensetype',
            name='company',
        ),
        migrations.RemoveField(
            model_name='transfermoneytype',
            name='company',
        ),
    ]

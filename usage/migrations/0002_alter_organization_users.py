# Generated by Django 4.1.5 on 2023-02-05 17:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('usage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]

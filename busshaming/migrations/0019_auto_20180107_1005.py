# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-07 10:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('busshaming', '0018_realtimeprogress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realtimeprogress',
            name='in_progress',
            field=models.DateTimeField(null=True),
        ),
    ]

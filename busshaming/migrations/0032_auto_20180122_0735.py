# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-22 07:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('busshaming', '0031_routedate_num_trips'),
    ]

    operations = [
        migrations.AddField(
            model_name='routedate',
            name='num_scheduled_trips',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='routedate',
            name='ontime_percent',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='routedate',
            name='scheduled_trip_early_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='routedate',
            name='scheduled_trip_late_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='routedate',
            name='scheduled_trip_ontime_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='routedate',
            name='scheduled_trip_ontime_percent',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='routedate',
            name='scheduled_trip_verylate_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='routedate',
            name='trip_early_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='routedate',
            name='trip_late_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='routedate',
            name='trip_ontime_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='routedate',
            name='trip_ontime_percent',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='routedate',
            name='trip_verylate_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-13 18:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0004_allow_empty_completed_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupchallenge',
            name='level',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='challenges.Level'),
            preserve_default=False,
        ),
    ]

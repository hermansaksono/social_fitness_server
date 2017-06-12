# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-12 23:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupStory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_current', models.BooleanField()),
                ('current_page', models.PositiveIntegerField(default=0)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('cover_url', models.URLField()),
                ('def_url', models.URLField()),
                ('slug', models.SlugField(max_length=25)),
            ],
        ),
        migrations.AddField(
            model_name='groupstory',
            name='story',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='story_manager.Story'),
        ),
    ]

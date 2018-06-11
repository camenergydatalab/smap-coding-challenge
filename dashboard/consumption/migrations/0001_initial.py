# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-03 05:31
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Consumption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(default=datetime.datetime.now)),
                ('consumption', models.DecimalField(decimal_places=2, default=None, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('area', models.CharField(default='a1', max_length=4)),
                ('tariff', models.CharField(default='t1', max_length=4)),
            ],
        ),
        migrations.AddField(
            model_name='consumption',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consumption.User'),
        ),
    ]
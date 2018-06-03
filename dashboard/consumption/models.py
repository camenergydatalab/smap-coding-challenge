# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    area = models.CharField(max_length=4, default='a1')
    tariff = models.CharField(max_length=4, default='t1')

class Consumption(models.Model):
    user = models.ForeignKey(User)
    datetime = models.DateTimeField(default=datetime.now)
    consumption = models.DecimalField(max_digits=6, decimal_places=2, null=True)
# Create your models here.

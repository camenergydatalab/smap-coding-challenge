# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class User(models.Model):
    area = models.CharField(max_length=10)
    tariff = models.CharField(max_length=10)


class Consumption(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    consumption = models.FloatField()

    class Meta:
        unique_together = ['user', 'datetime']


class CalculatedConsumption(models.Model):
    date = models.DateField()
    sum = models.FloatField()

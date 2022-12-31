# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class UserData(models.Model):
    area = models.CharField(max_length=255)
    tariff = models.CharField(max_length=255)


class ConsumptionData(models.Model):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE)
    datetime = models.DateTimeField(null=False, blank=False)
    consumption = models.FloatField(null=False, blank=False)

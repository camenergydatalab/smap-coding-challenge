# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    area = models.CharField(max_length=255)
    tariff = models.CharField(max_length=255)


class Consumption(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    amount = models.DecimalField(max_digits=5, decimal_places=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user_id", "datetime"], name="unique_user")
        ]
        db_table = "consumption_consumption"


class ConsumptionDetails(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user_id", "date"], name="unique_user")
        ]
        db_table = "consumption_consumptiondetails"

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class User(models.Model):
    """
    User data
    """
    id = models.IntegerField(
        primary_key=True,
        editable=False)
    area = models.CharField(
        "area",
        max_length=2)
    tariff = models.CharField(
        "tariff",
        max_length=2)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Consumption(models.Model):
    """
    Consumption data
    """
    id = models.IntegerField(
        primary_key=True,
        editable=False)
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE)
    datetime = models.DateTimeField(
        "datetime")
    consumption = models.DecimalField(
        "consumption",
        max_digits=10,  # NOTICE: should check max value
        decimal_places=1)

    class Meta:
        verbose_name = "Consumption"
        verbose_name_plural = "Consumption"

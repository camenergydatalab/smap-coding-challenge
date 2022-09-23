# -*- coding: utf-8 -*-
from django.db import models

PREFIX = "user_"


class Area(models.Model):
    """Area Model"""
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f"{PREFIX}areas"
        verbose_name_plural = "area"


class Tariff(models.Model):
    """Tariff Model"""
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f"{PREFIX}tariffs"
        verbose_name_plural = "tariff"


class User(models.Model):
    """User Model"""
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE)

    def __str__(self):
        return self.id

    class Meta:
        db_table = "users"
        verbose_name_plural = "user"


class Consumption(models.Model):
    """Consumption Model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    consumption = models.FloatField()

    def __str__(self):
        return self.id

    class Meta:
        db_table = f"{PREFIX}consumptions"
        ordering = ["-datetime"]
        verbose_name_plural = "consumption"

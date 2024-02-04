# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Area(models.Model):
    """エリア情報"""

    name = models.CharField(max_length=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Tariff(models.Model):
    """料金表情報"""

    plan = models.CharField(max_length=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.plan


class User(models.Model):
    """ユーザ情報"""

    id = models.PositiveIntegerField(primary_key=True, unique=True)
    area = models.ForeignKey(Area, unique=False, on_delete=models.PROTECT)
    tariff = models.ForeignKey(Tariff, unique=False, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class Consumption(models.Model):
    """消費データ"""

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    datetime = models.DateTimeField()
    value = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "datetime"], name="user_datetime_unique"
            ),
        ]

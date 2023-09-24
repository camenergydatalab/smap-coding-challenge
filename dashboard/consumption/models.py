# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class User(models.Model):
  id = models.IntegerField(primary_key=True)
  area = models.CharField(max_length=2, db_index=True)
  tariff = models.CharField(max_length=2, db_index=True)

class Consumption(models.Model):
  datetime = models.DateTimeField(db_index=True)
  consumption = models.FloatField()
  user = models.ForeignKey(User, on_delete=models.CASCADE)

# ユーザーごとの日別集計
class AggregateUserDailyConsumption(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  date = models.DateField(db_index=True)
  total_consumption = models.FloatField()
  average_consumption = models.FloatField()

  class Meta:
      # 特定の組み合わせの一意性制約
      unique_together = ('user', 'date')

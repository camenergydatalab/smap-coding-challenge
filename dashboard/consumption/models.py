# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pandas as pd
from django.db import models

# Create your models here.


class UserReport(models.Model):
    user_id = models.CharField(max_length=200)
    area = models.CharField(max_length=8)
    tariff = models.CharField(max_length=8)
    consumption_total = models.FloatField(default=0)
    consumption_avg = models.FloatField(default=0)

    def __str__(self):
        return self.user_id


class ConsumptionData:
    def __init__(self):
        self._df = pd.DataFrame(columns=["consumption"])

    def import_csv(self, csv_name):
        df = pd.read_csv(csv_name).drop_duplicates(subset="datetime")
        df.set_index("datetime", inplace=True)
        self._df = self._df.add(df, fill_value=0)

    def to_csv(self, csv_name):
        self._df.to_csv(csv_name)

    @property
    def total(self):
        return self._df["consumption"].sum()

    @property
    def avg(self):
        return self._df["consumption"].mean() * 2  # 0.5h/point

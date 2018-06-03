# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum, Max, Avg, Count
from datetime import datetime

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    area = models.CharField(max_length=4, default='a1')
    tariff = models.CharField(max_length=4, default='t1')

    def __str__(self):
        return str({ 'id': self.id, 'area': self.area, 'tariff': self.tariff })

    def aggregated_consumptions(self):
        return self.consumption_set.extra(select={
            'year': "date_part('year', datetime)",
            'month': "date_part('month', datetime)"
        }).values('year', 'month').annotate(
            sum=Sum('consumption'),
            max=Max('consumption'),
            average=Avg('consumption'),
            count=Count('consumption')
        ).order_by('year', 'month')

class Consumption(models.Model):
    user = models.ForeignKey(User)
    datetime = models.DateTimeField(default=datetime.now)
    consumption = models.DecimalField(max_digits=6, decimal_places=2, null=True)

    def __str__(self):
        return str({
            'id': self.id,
            'user': self.user_id,
            'datetime': self.datetime,
            'consumption': self.consumption
        })

    def year(self):
        return self.datetime.year

    def month(self):
        return self.datetime.month


# Create your models here.

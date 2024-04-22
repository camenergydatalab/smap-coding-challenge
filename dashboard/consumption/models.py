# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class User(models.Model):
    user_id = models.IntegerField(primary_key=True, verbose_name='ID')
    user_area = models.CharField(verbose_name='エリア', max_length=10)
    user_tariff = models.CharField(verbose_name='関税', max_length=10)
    created_at = models.DateTimeField(verbose_name='登録日', auto_now_add=True)

    class Meta:
        verbose_name_plural = 'User'

    def __int__(self):
        return self.user_id


class Consumption(models.Model):
    user_id = models.ForeignKey(User, models.DO_NOTHING, null=False)
    cousumption_datetime = models.DateTimeField(verbose_name='消費日時')
    cousumption_value = models.IntegerField(verbose_name='消費')
    created_at = models.DateTimeField(verbose_name='登録日', auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Consumption'

    def __int__(self):
        return self.user_id

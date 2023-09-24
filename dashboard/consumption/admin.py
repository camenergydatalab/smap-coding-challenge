# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import User,Consumption, AggregateUserDailyConsumption

# モデルを管理者ページに登録
admin.site.register(User)
admin.site.register(Consumption)
admin.site.register(AggregateUserDailyConsumption)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Area, Tariff, User, Consumption

admin.site.register(Area)
admin.site.register(Tariff)
admin.site.register(User)
admin.site.register(Consumption)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from consumption.models import User, Consumption

# Create your views here.


def summary(request):
    context = {
        'users': User.objects.order_by('id').all(),
    }
    return render(request, 'consumption/summary.html', context)


def detail(request):
    context = {
    }
    return render(request, 'consumption/detail.html', context)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Avg
from .models import User, AggregateUserDailyConsumption
from django.utils import timezone

def summary(request):
    users = User.objects.all()
    # 全ユーザーの日付別の合計と平均消費データを取得
    date_wise_consumption_data = AggregateUserDailyConsumption.objects.values('date').annotate(
        total_consumption=Sum('total_consumption'),
        average_consumption=Avg('average_consumption')
    )

    # テンプレートコンテキストにデータを渡す
    context = {
        'users': users,
        'date_wise_consumption_data': date_wise_consumption_data,
    }

    return render(request, 'consumption/summary.html', context)

def detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    date_wise_consumption_data = AggregateUserDailyConsumption.objects.filter(user=user)

    context = {
        'user': user,
        'date_wise_consumption_data': date_wise_consumption_data,
    }
    return render(request, 'consumption/detail.html', context)

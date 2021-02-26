# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from django.http import Http404
from django.db.models import Avg, Sum
from django.shortcuts import render

from .models import Consumption, User


def create_chart_data():
    labels = []
    total_data = []
    avg_data = []

    # aggregate consumption data
    consum_data = Consumption.objects.values('datetime').annotate(
        Avg('consumption'), Sum('consumption')).order_by('datetime')
    for consum in consum_data:
        labels.append(consum['datetime'].strftime("%Y-%m-%d %H:%M:%S"))
        total_data.append(str(consum['consumption__sum']))
        avg_data.append(str(consum['consumption__avg']))

    return {
        'labels': labels,
        'total_data': total_data,
        'avg_data': avg_data
    }


def create_table_data():
    data = []
    avg_consum_data = get_user_avg_consum()

    user_data = User.objects.all()
    for user in user_data:
        data.append({
            'id': user.id,
            'area': user.area,
            'tariff': user.tariff,
            'average': avg_consum_data[user.id]
        })

    min_value = min(data, key=lambda x: Decimal(x['average']))['average']
    max_value = max(data, key=lambda x: Decimal(x['average']))['average']

    return {
        'data': data,
        'min_value': min_value,
        'max_value': max_value,
    }


def get_user_avg_consum():
    avg_consum_data = {}

    consum_data = Consumption.objects.values('user_id').annotate(
        Avg('consumption'))
    for data in consum_data:
        avg_consum_data[data['user_id']] = str(data['consumption__avg'])

    return avg_consum_data


def summary(request):
    chart_data = create_chart_data()
    table_data = create_table_data()

    context = {
        'chart_data': chart_data,
        'table_data': table_data
    }

    return render(request, 'consumption/summary.html', context)


def detail(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Http404("User does not exist")

    chart_data = create_user_chart_data(user)

    context = {
        'user_id': user_id,
        'area': user.area,
        'tariff': user.tariff,
        'chart_data': chart_data
    }
    return render(request, 'consumption/detail.html', context)


def create_user_chart_data(user):
    labels = []
    data = []

    # aggregate consumption data
    consum_data = Consumption.objects.filter(user_id=user).order_by('datetime')
    for consum in consum_data:
        labels.append(consum.datetime.strftime("%Y-%m-%d %H:%M:%S"))
        data.append(str(consum.consumption))

    return {
        'labels': labels,
        'data': data,
    }

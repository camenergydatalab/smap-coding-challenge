# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.shortcuts import render

from .models import Consumption, User
from .services import (
    create_chart_data,
    create_table_data,
    create_user_chart_data,
)


def summary(request):
    """summary view

    Create Summary view.

    Returns:
        render function: Django render funciton

    Raises:
        Http404: if user or consumption data is not found
    """
    try:
        chart_data = create_chart_data()
        table_data = create_table_data()
    except Consumption.DoesNotExist:
        raise Http404("Consumption data does not exist")
    except User.DoesNotExist:
        raise Http404("User data does not exist")

    context = {
        'chart_data': {
            'labels': chart_data['labels'],
            'total_data': chart_data['total_data'],
            'avg_data': chart_data['avg_data']
        },
        'table_data': {
            'data': table_data['data'],
            'min_value': table_data['min_value'],
            'max_value': table_data['max_value'],
        }
    }

    return render(request, 'consumption/summary.html', context)


def detail(request, user_id):
    """detail view

    Create User's Detail view.

    Returns:
        render function: Django render funciton

    Raises:
        Http404: if user data is not found
    """
    try:
        user = User.objects.get(id=user_id)
        chart_data = create_user_chart_data(user)
    except User.DoesNotExist:
        raise Http404("User does not exist")

    context = {
        'user_id': user_id,
        'area': user.area,
        'tariff': user.tariff,
        'chart_data': chart_data
    }
    return render(request, 'consumption/detail.html', context)

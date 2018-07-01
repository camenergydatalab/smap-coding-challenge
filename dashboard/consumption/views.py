# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User, Consumption

def summary(request):
    context = {
        'users': User.objects.order_by('id').all(),
    }
    return render(request, 'consumption/summary.html', context)


def detail(request):
    context = {
    }
    return render(request, 'consumption/detail.html', context)

class ConsumptionGroupedByArea(APIView):
    def get(self, request, format=None):
        agg_type = request.query_params.get('agg_type').split('__')[0] or 'sum'
        consumptions = Consumption.aggregated_consumptions_by_area(agg_type=agg_type)
        columns = []
        columns.append(
            ['x'] + ["{}-{}".format(year, month) for year, month in consumptions.filter(user__area='a1').values_list('year', 'month')]
        )
        for area in User.objects.order_by('area').distinct('area').values_list('area', flat=True):
            agg_consumption = list(consumptions.filter(user__area=area).values_list("agg_consumption", flat=True))
            if request.query_params.get('agg_type').endswith('per_user'):
                user_count = list(consumptions.filter(user__area=area).values_list("user_count", flat=True))
                consumption_list = [x / y for (x, y) in zip(agg_consumption, user_count)]
            else:
                consumption_list = agg_consumption
            columns.append([area] + consumption_list)
        return Response({
            'bindto': '#chart',
            'type': 'line',
            'data': { 'x': 'x', 'xFormat': '%Y-%m', 'columns': columns },
            'axis': {
                'x': {
                    'type': 'timeseries',
                    'tick': {
                        'format': '%Y-%m'
                    },
                },
                'y': {
                    'label': "{}({})".format(agg_type, 'kWh' if agg_type == 'sum' else 'Wh'),
                },
            },
        })

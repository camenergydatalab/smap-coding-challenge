# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from .models import User, Consumption
from . import make_graph
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Avg, Q
from django.views.generic import ListView
from datetime import time


class SummaryView(ListView):
    model = User
    template_name = 'consumption/summary.html'

    def get_queryset(self):
        users = User.objects.all().order_by('user_id')
        return users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 全ユーザー月別総消費量合計情報取得
        queryset = Consumption.objects.annotate(
            month=TruncMonth('cousumption_datetime')
        ).values('month').annotate(
            total_value=Sum('cousumption_value')
        ).order_by('month')

        # グラフ化
        x_list = []
        y_list = []
        for data in queryset:
            x_list.append(data['month'].strftime('%Y/%m'))
            y_list.append(int(data['total_value']))

        graph_image = make_graph.Plot_Graph(x_list, y_list, "Month", "Consumption")
        context['chart_1'] = graph_image

        # エリア別消費比率
        queryset = Consumption.objects.values("user_id__user_area").annotate(
            area_total=Sum("cousumption_value")
        )

        # グラフ化
        label_list = []
        x_list = []
        for data in queryset:
            label_list.append(data['user_id__user_area'])
            x_list.append(int(data['area_total']))

        graph_image = make_graph.Plot_Graph(x_list, label_list, None, None, 2)
        context['chart_2'] = graph_image

        return context


def detail(request, user_id):
    # 月別消費量合計
    queryset = Consumption.objects.filter(user_id=user_id).annotate(
        month=TruncMonth('cousumption_datetime')
    ).values('month').annotate(
        total_value=Sum('cousumption_value')
    ).order_by('month')

    # グラフ化
    x = [data['month'].strftime('%Y/%m') for data in queryset]
    y = [int(data['total_value']) for data in queryset]
    graph_image_1 = make_graph.Plot_Graph(x, y, "Month", "Consumption")

    # 時間帯別平均使用量
    y_list = []
    for i in range(4):
        start_time = time(i * 6, 0, 0)
        end_time = time(i * 6 + 5, 0, 0)
        queryset = Consumption.objects.filter(user_id=user_id).filter(
            Q(cousumption_datetime__time__gte=start_time) &
            Q(cousumption_datetime__time__lte=end_time)
        ).aggregate(Avg('cousumption_value'))
        y_list.append(queryset['cousumption_value__avg'])

    # グラフ化
    x = ['00:00-06:00', '06:00-12:00', '12:00-18:00', '18:00-24:00']
    y = y_list
    graph_image_2 = make_graph.Plot_Graph(x, y, "Time zone", "Consumption")

    context = {
        'user_id': user_id,
        'chart_1': graph_image_1,
        'chart_2': graph_image_2
    }
    return render(request, 'consumption/detail.html', context)

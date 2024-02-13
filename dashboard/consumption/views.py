# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.shortcuts import get_object_or_404, render

from .models import User
from .repository.consumption_repository import ConsumptionRepository
from .repository.user_repository import UserRepository


# Create your views here.
def summary(request):
    users = UserRepository.get_all()

    # 集計期間の取得
    total_period_months = ConsumptionRepository.get_total_period_months()

    # 集計期間の開始日と終了日を取得
    start_end_day = ConsumptionRepository.get_period_start_end_day()

    total_value_chart_datasets = []
    daily_average_value_chart_datasets = []

    if total_period_months.count:
        # 月別消費量合計
        total_value_per_month = ConsumptionRepository.get_total_value_per_month()

        total_value_chart_datasets.append(
            {
                "label": "月別 消費量合計",
                "data": list(map(str, list(total_value_per_month.values()))),
                "borderWidth": 2,
            }
        )

        # 月別1日あたりの平均消費量
        daily_average_value_per_month = (
            ConsumptionRepository.get_daily_average_value_per_month()
        )

        daily_average_value_chart_datasets.append(
            {
                "label": "月別 1日あたりの総消費量の平均値",
                "data": list(map(str, list(daily_average_value_per_month.values()))),
                "borderWidth": 2,
            }
        )

    total_value_chart_data = {
        "labels": total_period_months,
        "datasets": total_value_chart_datasets,
    }

    daily_average_value_chart_data = {
        "labels": total_period_months,
        "datasets": daily_average_value_chart_datasets,
    }

    context = {
        "start_end_day": start_end_day,
        "users": users,
        "total_value_chart_data": json.dumps(total_value_chart_data),
        "daily_average_value_chart_data": json.dumps(daily_average_value_chart_data),
    }

    return render(request, "consumption/summary.html", context)


def detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    # 集計期間の取得
    total_period_months = ConsumptionRepository.get_total_period_months()

    # 集計期間の開始日と終了日を取得
    start_end_day = ConsumptionRepository.get_period_start_end_day()

    total_value_chart_datasets = []
    daily_average_value_chart_datasets = []

    if total_period_months.count:
        # ユーザごとの月別消費量合計
        total_value_per_month = (
            ConsumptionRepository.get_total_value_per_month_by_user_id(user)
        )

        total_value_chart_datasets.append(
            {
                "label": "ユーザID : " + str(user),
                "data": list(map(str, list(total_value_per_month.values()))),
                "borderWidth": 2,
            }
        )

        # ユーザごとの1日あたりの平均消費量
        daily_average_value_per_month = (
            ConsumptionRepository.get_daily_average_value_per_month_by_user_id(user)
        )

        daily_average_value_chart_datasets.append(
            {
                "label": "ユーザID : " + str(user),
                "data": list(map(str, list(daily_average_value_per_month.values()))),
                "borderWidth": 2,
            }
        )

    total_value_chart_data = {
        "labels": total_period_months,
        "datasets": total_value_chart_datasets,
    }

    daily_average_value_chart_data = {
        "labels": total_period_months,
        "datasets": daily_average_value_chart_datasets,
    }

    context = {
        "start_end_day": start_end_day,
        "user": user,
        "total_value_chart_data": json.dumps(total_value_chart_data),
        "daily_average_value_chart_data": json.dumps(daily_average_value_chart_data),
    }

    return render(request, "consumption/detail.html", context)

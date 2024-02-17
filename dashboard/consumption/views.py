# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.db.models import Avg, Sum
from .models import User, Consumption, ConsumptionDetails
import plotly.graph_objects as go
from typing import List, Any
from datetime import date
from decimal import Decimal
import pandas as pd


def _create_plot_fig(dates: List[date], total_consumptions: List[Decimal]) -> Any:
    """グラフを作成する

    Args:
        dates (List[date]): 日付のリスト
        total_consumptions (List[Decimal]): 合計値のリスト

    Returns:
        Any: 図のHTML
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=total_consumptions))
    fig.update_layout(
        title="日ごとのエネルギー総消費量",
        xaxis_title="日付",
        yaxis_title="合計消費量(Wh)",
    )
    return fig.to_html(fig, include_plotlyjs=False)


def summary(request):
    users = User.objects.all()
    user_ids = []
    total_consumptions = []
    dates = list(
        ConsumptionDetails.objects.filter(user=users[0].id).values_list(
            "date", flat=True
        )
    )
    for user in users:
        user_ids.append(user.id)
        consumptions = Consumption.objects.filter(user=user)
        user.total_consumption = consumptions.aggregate(Sum("amount"))["amount__sum"]
        user.average_consumption = consumptions.aggregate(Avg("amount"))["amount__avg"]
    for d in dates:
        consumption_details = ConsumptionDetails.objects.filter(date=d)
        total_consumptions.append(
            consumption_details.aggregate(Sum("total"))["total__sum"]
        )
    plot_fig = _create_plot_fig(dates, total_consumptions)
    context = {"users": users, "graph": plot_fig}
    return render(request, "consumption/summary.html", context)


def detail(request):
    user_id = request.GET.get("id")
    consumptions = ConsumptionDetails.objects.filter(user=user_id)
    df = pd.DataFrame(consumptions.values("date", "total"))
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    monthly_data = []
    for m, row in df.resample("ME").sum().iterrows():
        monthly_data.append({"month": m.strftime("%Y-%m"), "total_sum": row["total"]})
    plot_data = list(consumptions.values_list("date", "total"))
    dates, totals = [list(tup) for tup in zip(*plot_data)]
    plot_fig = _create_plot_fig(dates, totals)
    context = {
        "user_id": user_id,
        "monthly_data": monthly_data,
        "graph": plot_fig,
    }
    return render(request, "consumption/detail.html", context)

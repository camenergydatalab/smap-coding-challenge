# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import pandas as pd
from consumption.consts import CONSUMPTION_CACHE_KEY
from consumption.models.master import Area
from consumption.utils.cache_utils import cache_consumption_data
from django.core.cache import cache
from django.shortcuts import render

# Create your views here.


def summary(request):
    """集計画面の表示ビュー
    Args:
        request (HttpRequest): Django リクエストオブジェクト
    Returns:
        HttpResponse: レスポンスオブジェクト
    Note:
        直近1カ月のキャッシュデータからエリア、曜日、時間帯ごとに合計消費量を算出する
    Todo:
        変数名が検討しきれていない
        area_〇〇_values作成処理の共通化を検討しきれていない + モジュール化したい
    """
    # キャッシュデータが存在しない場合、キャッシュのセット処理を呼び出す
    if CONSUMPTION_CACHE_KEY not in cache:
        cache_consumption_data()
    consumption_result_df: pd.DataFrame = cache.get(CONSUMPTION_CACHE_KEY)

    # 消費量の集計グラフ表示用データの作成処理
    weekday_list = []
    holiday_list = []
    grouped_by_consumption_result_df = consumption_result_df.groupby(
        ["is_holiday", "area__area_name", "time_of_day"]
    ).agg({"consumption_amount": "sum"})
    area_names = Area.objects.values_list("area_name", flat=True)
    for area_name in area_names:
        # データフレームに該当するエリア名のデータが存在しない場合はスキップ
        if not (False, area_name) in grouped_by_consumption_result_df.index:
            continue
        area_weekday_values = (
            grouped_by_consumption_result_df.loc[(False, area_name)]
            .reset_index()
            .set_index("time_of_day")["consumption_amount"]
            .astype(float)
            .to_dict()
        )
        weekday_list.append({area_name: area_weekday_values})
        area_holiday_values = (
            grouped_by_consumption_result_df.loc[(True, area_name)]
            .reset_index()
            .set_index("time_of_day")["consumption_amount"]
            .astype(float)
            .to_dict()
        )
        holiday_list.append({area_name: area_holiday_values})
    # ユーザ一覧表の表示用データ作成処理
    user_data_list = (
        consumption_result_df.groupby(["user_id", "area__area_name", "tariff_plan__plan_name"])
        .agg({"consumption_amount": "sum"})
        .astype(float)
        .reset_index()
        .to_dict("records")
    )
    context = {
        "weekdayList": json.dumps(weekday_list),
        "holidayList": json.dumps(holiday_list),
        "userDataList": user_data_list,
    }
    return render(request, "consumption/summary.html", context)


def detail(request, user_id):
    """詳細画面の表示ビュー
    Args:
        request (HttpRequest): Django リクエストオブジェクト
        user_id: 対象ユーザのユーザID
    Returns:
        HttpResponse: レスポンスオブジェクト
    Note:
        直近1カ月のキャッシュデータから対象ユーザの曜日、時間帯ごとの合計消費量を算出する
    Todo:
        変数名が検討しきれていない
        area_〇〇_values作成処理の共通化を検討しきれていない + モジュール化したい
    """
    # キャッシュデータが存在しない場合、キャッシュのセット処理を呼び出す
    if CONSUMPTION_CACHE_KEY not in cache:
        cache_consumption_data()
    consumption_result_df: pd.DataFrame = cache.get(CONSUMPTION_CACHE_KEY)

    # ユーザのグラフ表示用データの作成
    grouped_by_consumption_result_df = (
        consumption_result_df.query("user_id == @user_id")
        .groupby(["is_holiday", "time_of_day"])
        .agg({"consumption_amount": "sum"})
    )
    weekday_list = {
        user_id: (
            grouped_by_consumption_result_df.query("is_holiday == False")
            .reset_index()
            .set_index("time_of_day")["consumption_amount"]
            .astype(float)
            .to_dict()
        )
    }
    holiday_list = {
        user_id: (
            grouped_by_consumption_result_df.query("is_holiday == True")
            .reset_index()
            .set_index("time_of_day")["consumption_amount"]
            .astype(float)
            .to_dict()
        )
    }
    context = {"weekdayList": json.dumps([weekday_list]), "holidayList": json.dumps([holiday_list]), "user_id": user_id}
    return render(request, "consumption/detail.html", context)

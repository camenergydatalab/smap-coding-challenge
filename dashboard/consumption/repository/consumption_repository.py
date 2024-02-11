# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pandas as pd
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django_pandas.io import read_frame

from ..models import Consumption


class ConsumptionRepository:
    @staticmethod
    def bulk_insert(consumption_models=[]):
        """消費データの一括登録
        引数:
            consumption_models: Consumptionモデルのオブジェクト
        戻り値:
            なし
        """
        if len(consumption_models):
            Consumption.objects.bulk_create(consumption_models)

    @staticmethod
    def get_total_period_months():
        """全集計期間月を取得しリストで返却する
        引数:
            なし
        戻り値:
            %Y-%m形式にフォーマットした年月文字列のリスト
        """
        consumption_queryset = (
            Consumption.objects.distinct()
            .annotate(month_year=TruncMonth("datetime"))
            .values("month_year")
        )

        formatted_dates = []

        for consumption in consumption_queryset:
            formatted_dates.append(consumption["month_year"].strftime("%Y-%m"))

        return formatted_dates

    @staticmethod
    def calc_total_value_per_month(consumption_qs):
        """Pandasを利用して、Consumptionクラスのクエリセットから月別消費量を計算する
        引数
            consumption_qs: datetime と value の値を持つConsumptionクラスのクエリセット
        戻り値:
            %Y-%m形式にフォーマットした年月文字列をKeyとして、valueに使用量の合計値をもつdict型データ
        """
        total_value_per_month = {}

        if consumption_qs.count():
            consumption_df = read_frame(consumption_qs)
            consumption_df["year_month"] = consumption_df["datetime"].dt.strftime(
                "%Y-%m"
            )
            consumption_df.set_index("year_month")

            total_value_per_month_series = consumption_df.groupby("year_month")[
                "value"
            ].sum()

            for year_month, total_value in total_value_per_month_series.items():
                total_value_per_month[year_month] = total_value

        return total_value_per_month

    @staticmethod
    def calc_daily_average_value_per_month(consumption_qs):
        """Pandasを利用して、Consumptionクラスのクエリセットから月別の平均消費量を計算する
        引数
            consumption_qs: datetime と value の値を持つConsumptionクラスのクエリセット
        戻り値:
            %Y-%m形式にフォーマットした年月文字列をKeyとして、valueに使用量の平均消費量をもつdict型データ
        """
        daily_average_value_per_month = {}

        if consumption_qs.count():
            consumption_df = read_frame(consumption_qs)
            consumption_df["year_month"] = consumption_df["datetime"].dt.strftime(
                "%Y-%m"
            )
            consumption_df.set_index("year_month")

            daily_average_value_per_month_series = consumption_df.groupby("year_month")[
                "value"
            ].mean()

            for year_month, total_value in daily_average_value_per_month_series.items():
                daily_average_value_per_month[year_month] = total_value

        return daily_average_value_per_month

    @staticmethod
    def get_total_value_per_month():
        """月別消費量を取得
        引数
            なし
        戻り値:
            %Y-%m形式にフォーマットした年月文字列をKeyとして、valueに使用量の合計値をもつdict型データ
        """
        consumption_qs = Consumption.objects.all().values("datetime", "value")

        return ConsumptionRepository.calc_total_value_per_month(consumption_qs)

    @staticmethod
    def get_daily_average_value_per_month():
        """月別1日あたりの平均消費量を取得
        引数
            なし
        戻り値:
            %Y-%m形式にフォーマットした年月文字列をKeyとして、valueに使用量の平均消費量をもつdict型データ
        """
        consumption_qs = Consumption.objects.all().values("datetime", "value")

        return ConsumptionRepository.calc_daily_average_value_per_month(consumption_qs)

    @staticmethod
    def get_total_value_per_month_by_user_id(user_model):
        """ユーザごとに月別消費量を取得
        引数
            user_model: Userモデルのオブジェクト
        戻り値:
            %Y-%m形式にフォーマットした年月文字列をKeyとして、valueに使用量の合計値をもつdict型データ
        """
        consumption_qs = Consumption.objects.filter(user=user_model).values(
            "datetime", "value"
        )

        return ConsumptionRepository.calc_total_value_per_month(consumption_qs)

    @staticmethod
    def get_total_value_by_user_id(user_model):
        """ユーザごとに月別消費量を取得
        引数
            user_model: Userモデルのオブジェクト
        戻り値:
            value の合計値
        """
        return Consumption.objects.filter(user=user_model).aggregate(
            total_value=Sum("value")
        )["total_value"]

    @staticmethod
    def get_daily_average_value_per_month_by_user_id(user_model):
        """ユーザごとに月別1日あたりの平均消費量を取得
        引数
            user_model: Userモデルのオブジェクト
        戻り値:
            %Y-%m形式にフォーマットした年月文字列をKeyとして、valueに使用量の平均消費量をもつdict型データ
        """
        consumption_qs = Consumption.objects.filter(user=user_model).values(
            "datetime", "value"
        )

        return ConsumptionRepository.calc_daily_average_value_per_month(consumption_qs)

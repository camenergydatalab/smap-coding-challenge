# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pandas as pd
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth
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
    def get_period_start_end_day():
        """集計期間の開始日と終了日を返す
        引数:
            なし
        戻り値:
            以下の形式のDict型データ
            {
                'start': YYYY-MM-DD,
                'end': YYYY-MM-DD,
            }
        """
        consumption_qs = (
            Consumption.objects.distinct()
            .annotate(day=TruncDay("datetime"))
            .values("day")
        )

        formatted_days = {
            "start": "",
            "end": "",
        }

        if consumption_qs.count():
            start_day = consumption_qs.first()
            end_day = consumption_qs.last()

            formatted_days = {
                "start": start_day["day"].strftime("%Y-%m-%d"),
                "end": end_day["day"].strftime("%Y-%m-%d"),
            }

        return formatted_days

    @staticmethod
    def get_total_period_months():
        """全集計期間月を取得しリストで返す
        引数:
            なし
        戻り値:
            %Y-%m形式にフォーマットした年月文字列のリスト
        """
        consumption_qs = (
            Consumption.objects.distinct()
            .annotate(year_month=TruncMonth("datetime"))
            .values("year_month")
        )

        formatted_dates = []

        for consumption in consumption_qs:
            formatted_dates.append(consumption["year_month"].strftime("%Y-%m"))

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

            total_value_per_month_series = consumption_df.groupby("year_month")[
                "value"
            ].sum()

            for year_month, total_value in total_value_per_month_series.items():
                total_value_per_month[year_month] = total_value

        return total_value_per_month

    @staticmethod
    def calc_daily_average_value_per_month(consumption_qs):
        """Pandasを利用して、Consumptionクラスのクエリセットから月別の1日あたりの総消費量の平均値を計算する
        引数
            consumption_qs: datetime と value の値を持つConsumptionクラスのクエリセット
        戻り値:
            %Y-%m形式にフォーマットした年月文字列をKeyとして、valueに1日あたりの総消費量の平均値をもつdict型データ
        """
        daily_average_value_per_month = {}

        if consumption_qs.count():
            consumption_df = read_frame(consumption_qs)
            consumption_df["date"] = consumption_df["datetime"].dt.date

            total_value_per_month_series = consumption_df.groupby("date")["value"].sum()

            # Series to Dataframe
            total_value_per_month_df = total_value_per_month_series.reset_index()

            total_value_per_month_df["year_month"] = pd.to_datetime(
                total_value_per_month_df["date"]
            ).dt.strftime("%Y-%m")

            daily_average_value_per_month_series = total_value_per_month_df.groupby(
                "year_month"
            )["value"].mean()

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

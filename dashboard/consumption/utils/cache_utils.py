import datetime
import logging
from typing import List

import jpholiday
import pandas as pd
from consumption.consts import CONSUMPTION_CACHE_KEY
from consumption.models.user_related import User, UserConsumptionHistory, UserContractHistory
from django.conf import settings
from django.core.cache import cache
from django_pandas.io import read_frame


def cache_consumption_data() -> None:
    """消費量データのキャッシュ処理"""
    logging.info("cache_consumption_summary_data has started")
    # TODO 本来であれば本日から1か月前までを対象期間とするが、データの関係上1か月間の期間はハードコーディングする
    start_date = datetime.date(2016, 12, 1)
    end_date = datetime.date(2016, 12, 31)
    # User関連データを連結したデータフレームを作成する
    consumption_result_df = create_merged_consumption_result_df(start_date, end_date)

    # TODO 分割したい
    # 平日か休日(祝日含む)か判定
    holidays: List = jpholiday.between(start_date, end_date)
    consumption_result_df["is_holiday"] = (consumption_result_df["measurement_at"].dt.dayofweek >= 5) | (
        consumption_result_df["measurement_at"].isin(holidays)
    )

    # 時間帯判別処理
    # 深夜（0:00~5:00）、 朝（05:00~10:00）, 昼（10:00~15:00）, 夕方（15:00~19:00）, 夜（19:00~24:00）
    bins = [-1, 5, 10, 15, 19, 25]
    labels = ["late_night", "morning", "daytime", "evening", "night"]
    consumption_result_df["time_of_day"] = pd.cut(
        consumption_result_df["measurement_at"].dt.hour, bins=bins, labels=labels, right=False
    )
    cache.set(CONSUMPTION_CACHE_KEY, consumption_result_df, timeout=60 * 60)
    logging.info("cache_consumption_summary_data has finished")


def create_merged_consumption_result_df(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """ユーザデータをmergeしたデータフレームの作成処理
    Args:
        start_date: サマリーデータ算出開始日
        end_date: サマリーデータ算出終了日
    Return:
        consumption_result_df: ユーザデータをmergeしたデータフレーム
    """
    # TODO 契約期間に応じたデータ取得に変えたいが実装できず…
    logging.info("create_merged_user_data_df has started")
    # テーブル情報の取得
    user_data = User.objects.values("user_id")
    consumption_history_data = UserConsumptionHistory.objects.values(
        "user__user_id", "measurement_at", "consumption_amount"
    ).filter(measurement_at__range=(start_date, end_date))
    contract_history_data = UserContractHistory.objects.values(
        "user__user_id", "area__area_name", "tariff_plan__plan_name", "contract_start_at", "contract_end_at"
    ).filter(contract_end_at__isnull=True)
    # テーブル情報をまとめたデータフレームの作成
    user_df = read_frame(user_data)
    consumption_history_df = read_frame(consumption_history_data)
    contract_history_df = read_frame(contract_history_data)
    # データフレームをmergeする
    consumption_result_df = pd.merge(contract_history_df, user_df, left_on="user__user_id", right_on="user_id")
    consumption_result_df = pd.merge(consumption_result_df, consumption_history_df, on="user__user_id")
    # consumption_result_df = merged_df[['user_id', 'area__area_name', 'measurement_at', 'consumption_amount']]
    consumption_result_df["measurement_at"] = consumption_result_df["measurement_at"].dt.tz_convert(settings.TIME_ZONE)
    logging.info("create_merged_user_data_df has finished")
    return consumption_result_df

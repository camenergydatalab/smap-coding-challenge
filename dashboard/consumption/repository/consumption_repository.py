# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..models import Consumption


class ConsumptionRepository:
    @staticmethod
    def bulk_insert(consumptions=[]):
        """消費データの一括登録
        引数:
            consumptions: 以下の構造の辞書データの配列
                user: ユーザオブジェクト
                datetime: datetime.datetimeの日時オブジェクト
                value: 消費量
        """

        if len(consumptions):
            consumption_models = []

            for c in consumptions:
                consumption_models.append(
                    Consumption(
                        user=c["user"], datetime=c["datetime"], value=c["value"]
                    )
                )

            Consumption.objects.bulk_create(consumption_models)

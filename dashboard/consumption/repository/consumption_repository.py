# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..models import Consumption


class ConsumptionRepository:
    @staticmethod
    def bulk_insert(consumption_models=[]):
        """消費データの一括登録
        引数:
            consumption_models: Consumptionモデルのオブジェクト
        """

        if len(consumption_models):
            Consumption.objects.bulk_create(consumption_models)

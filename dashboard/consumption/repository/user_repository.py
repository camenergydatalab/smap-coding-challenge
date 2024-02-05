# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..models import User


class UserRepository:
    @staticmethod
    def bulk_insert(users=[]):
        """ユーザデータの一括登録
        引数:
            users: 以下の構造の辞書データの配列
                id: ユーザID
                area: エリアのオブジェクトデータ
                tariff: 料金表のオブジェクトデータ
        """

        if len(users):
            user_models = []

            for u in users:
                user_models.append(User(id=u["id"], area=u["area"], tariff=u["tariff"]))

            User.objects.bulk_create(user_models)

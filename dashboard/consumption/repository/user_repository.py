# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..models import User


class UserRepository:
    @staticmethod
    def bulk_insert(user_models=[]):
        """ユーザデータの一括登録
        引数:
            user_models: Userモデルのオブジェクト
        """

        if len(user_models):
            User.objects.bulk_create(user_models)

    @staticmethod
    def get_all():
        """すべてのユーザデータを取得する
        戻り値:
            User.objects.all()のクエリセット
        """
        return User.objects.all().order_by("id")

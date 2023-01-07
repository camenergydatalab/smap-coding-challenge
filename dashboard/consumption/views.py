# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.functions import TruncDate
from django.http import Http404
from django.utils.functional import cached_property
from django.views import generic

from consumption.models import ConsumptionData, UserData


class SummaryView(generic.ListView):
    """ユーザリストと全消費量データの合計と平均グラフを表示するViewクラス"""
    template_name = "consumption/summary.html"
    model = UserData
    ordering = ["pk"]
    paginate_by = 20
    context_object_name = "users"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["aggregate_consumption"] = aggregate_consumption()
        return ctx


def aggregate_consumption():
    qs = ConsumptionData.objects.all()
    qs = qs.annotate(date=TruncDate("datetime"))
    qs = qs.order_by("date")
    qs = qs.values("date")
    return qs.annotate(
        total=models.Sum("consumption"), average=models.Avg("consumption")
    )


class UserDetailView(generic.DetailView):
    """ユーザの消費量データを1日毎にグラフ表示するViewクラス
    日付が指定された場合、その日の消費量データを表示する。

    /detail/3000/?current_date=2023-01-01
    => ユーザID3000 の 2023-01-01の消費量データを表示する
    """
    model = UserData
    template_name = "consumption/detail.html"
    pk_url_kwarg = "user_id"
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        try:
            prev_date, next_date = get_before_and_after_date(
                self.date_list, self.current_date
            )
        except ValueError:
            # 消費量データがない日付がしてされたとき404エラーを返す。
            raise Http404("無効な日付です。")

        ctx = super().get_context_data(**kwargs)

        ctx["date_list"] = self.date_list
        ctx["consumption_list"] = self.get_user_consumption_data()
        ctx["current_date"] = self.current_date
        ctx["prev_date"] = prev_date
        ctx["next_date"] = next_date

        return ctx

    @cached_property
    def date_list(self):
        """ユーザの消費量データのdatetimeから日付のみを昇順リストとして返す。

        :return: list[str]
            ["2023-01-01", "2023-01-02", "2023-01-03", ]
        """
        user = self.get_object()
        date_list = (
            user.consumptiondata_set.all()
            .annotate(date=TruncDate("datetime"))
            .values_list("date", flat=True)
            .order_by("date")
            .distinct()
        )
        date_list = [str(d) for d in date_list]
        return date_list

    @property
    def current_date(self):
        """詳細ページで指定された日時を返す。指定されていない場合はdate_listから最新日を返す。

        :return: str|None
            "2023-01-01" or None
        """
        date_list = self.date_list
        try:
            latest_date = date_list[-1]
        except IndexError:
            latest_date = None

        current_date = self.request.GET.get("current_date", latest_date)
        return current_date

    def get_user_consumption_data(self):
        """ユーザの指定された日付の消費量データを返す。"""
        user = self.get_object()
        current_date = self.current_date

        if current_date:
            user_consumption = user.consumptiondata_set.filter(
                datetime__date=current_date
            ).order_by("datetime")
        else:
            user_consumption = ConsumptionData.objects.none()

        return user_consumption


def get_before_and_after_date(date_list, current_date):
    """
    日付のリスト(date_list)から指定された日付(current_date)の前後の値を返す。
    date_listが空リストの場合は (None, None) を返す。
    ---
    date_list: ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"]
    current_date: "2023-01-04" -> ("2023-01-03", None)
    current_date: "2023-01-03" -> ("2023-01-02", "2023-01-04")
    current_date: "2023-01-01" -> (None, "2023-01-02")
    ---

    :return:
    """

    prev_date, _, next_date = get_prev_next_items_from_list(date_list, current_date)
    return prev_date, next_date


def get_prev_next_items_from_list(list_data, target_item):
    """
    リスト(list_data)から指定された値(target_item)とその前後の値を返す。
    ---
    list_data: [1, 2, 3, 4]
    current_date: 4 -> (3, 4, None)
    current_date: 3 -> (2, 3, 4)
    current_date: 1 -> (None, 1, 2)
    ---

    :param list_data: list[T]
    :param target_item: T

    :return:
    prev_date: T|None
    next_date: T|None
    """

    if len(list_data) < 1:
        return None, target_item, None

    list_data = [None] + list_data + [None]
    date_index = list_data.index(target_item)

    prev_item, target_item, next_item = list_data[(date_index - 1): (date_index + 2)]
    return prev_item, target_item, next_item

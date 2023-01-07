# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.functions import TruncDate
from django.http import Http404
from django.utils.functional import cached_property
from django.views import generic

from consumption.models import ConsumptionData, UserData


class SummaryView(generic.ListView):
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
        total=models.Sum("consumption"),
        average=models.Avg("consumption")
    )


class UserDetailView(generic.DetailView):
    model = UserData
    template_name = "consumption/detail.html"
    pk_url_kwarg = "user_id"
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        try:
            prev_date, next_date = get_prev_and_next_date(self.date_list, self.current_date)
        except ValueError:
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
        user = self.get_object()
        date_list = user.consumptiondata_set.all() \
            .annotate(date=TruncDate("datetime")) \
            .values_list("date", flat=True) \
            .order_by("-date") \
            .distinct()
        date_list = [str(d) for d in date_list]
        return date_list

    @property
    def current_date(self):
        date_list = self.date_list
        try:
            latest_date = date_list[0]
        except IndexError:
            latest_date = None

        current_date = self.request.GET.get('current_date', latest_date)
        return current_date

    def get_user_consumption_data(self):
        user = self.get_object()
        current_date = self.current_date

        if current_date:
            user_consumption = user.consumptiondata_set.filter(datetime__date=current_date).order_by("datetime")
        else:
            user_consumption = ConsumptionData.objects.none()

        return user_consumption


def get_prev_and_next_date(date_list, current_date):
    """
    :param date_list: list
    :param current_date: str

    :return:
    prev_date: str|None
    next_date: str|None
    """

    if len(date_list) < 1:
        return None, None

    date_list = [None] + date_list + [None]
    date_index = date_list.index(current_date)
    next_date, c, prev_date = date_list[(date_index - 1):(date_index + 2)]
    return prev_date, next_date

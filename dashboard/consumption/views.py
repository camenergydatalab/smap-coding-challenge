# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.db.models.functions import TruncDate
from django.http import Http404
from django.shortcuts import render, get_object_or_404

from consumption.models import ConsumptionData, UserData


def summary(request):
    users = all_users()
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page', 1)

    try:
        pages = paginator.page(page_number)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(1)

    context = {
        'aggregate_consumption': aggregate_consumption(),
        'users': pages.object_list,
        "pages": pages,
        'paginator': paginator,
        'is_paginated': pages.has_other_pages(),
        'object_list': pages.object_list,
    }
    return render(request, 'consumption/summary.html', context)


def aggregate_consumption():
    qs = ConsumptionData.objects.all()
    qs = qs.annotate(date=TruncDate("datetime"))
    qs = qs.order_by("date")
    qs = qs.values("date")
    return qs.annotate(
        total=models.Sum("consumption"),
        average=models.Avg("consumption")
    )


def all_users():
    return UserData.objects.all().order_by("id")


def detail(request, user_id):
    user = get_object_or_404(UserData, pk=user_id)
    try:
        date_list = user.consumptiondata_set.all() \
            .annotate(date=TruncDate("datetime")) \
            .values_list("date", flat=True) \
            .order_by("-date") \
            .distinct()
        date_list = [str(d) for d in date_list]

        try:
            latest_date = date_list[0]
        except IndexError:
            latest_date = None

        current_date = request.GET.get('current_date', latest_date)
        prev_date, next_date = get_prev_and_next_date(date_list, current_date)

        if current_date:
            user_consumption = user.consumptiondata_set.filter(datetime__date=current_date).order_by("datetime")
        else:
            user_consumption = ConsumptionData.objects.none()

    except:
        raise Http404()

    context = {
        "user": user,
        "consumption_list": user_consumption,
        'date_list': date_list,
        'current_date': current_date,
        'prev_date': prev_date,
        'next_date': next_date
    }
    return render(request, 'consumption/detail.html', context)


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


def detail_(request, user_id):
    user = get_object_or_404(UserData, pk=user_id)
    user_consumption = user.consumptiondata_set.all().order_by("datetime").reverse()

    paginator = Paginator(user_consumption, 48)
    page_number = request.GET.get('page', 1)

    try:
        pages = paginator.page(page_number)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(1)

    context = {
        "user": user,
        "consumption_list": pages.object_list,
        "pages": pages,
        'paginator': paginator,
        'page_obj': pages,
        'is_paginated': pages.has_other_pages(),
        'object_list': pages.object_list
    }
    return render(request, 'consumption/detail.html', context)

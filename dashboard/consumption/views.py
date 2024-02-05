# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import datetime
from django.db import connection
from django.shortcuts import render
from django.urls import reverse
from functools import partial
from sqlalchemy import select, func, and_, literal_column
from sqlalchemy.dialects.sqlite import dialect as _sqlite_dialect
from typing import Optional, Union

from .models import Consumer, consumption_table, consumer_table
from .utils import explicitly_cached, make_json_response

# make django happy
sqlite_dialect = _sqlite_dialect(paramstyle="format")

AggDataRow = tuple[datetime, Union[int, float], int]


def summary(request):
    area = request.GET.get("area")
    tariff = request.GET.get("tariff")
    consumers = list(Consumer.objects.all())
    agg_func = agg_func_from_request(request)
    agg_data = agg_func(area=area, tariff=tariff)
    areas = sorted(set(map(lambda x: x.area, consumers)))
    tariffs = sorted(set(map(lambda x: x.tariff, consumers)))
    context = {
        "consumers": consumers,
        "agg_data_json": json.dumps(agg_data),
        "area": area,
        "areas": areas,
        "tariff": tariff,
        "tariffs": tariffs,
        "query_path": reverse("query"),
    }
    return render(request, 'consumption/summary.html', context)


def detail(request, id):
    context = {
    }
    return render(request, 'consumption/detail.html', context)


def query(request):
    try:
        agg_func = agg_func_from_request(request)
        consumer_id = request.GET.get("consumer_id")
        if consumer_id:
            try:
                consumer_id = int(consumer_id)
            except ValueError:
                return make_json_response(
                    None, status=400, errno=255,
                    message="consumer_id must be an integer")
            agg_data = agg_func(consumer_id=consumer_id)
        else:
            agg_data = agg_func(area=request.GET.get("area"),
                                tariff=request.GET.get("tariff"))
    except Exception:
        return make_json_response(None, status=500, errno=255,
                                  message="internal server error")
    return make_json_response(agg_data)


def agg_func_from_request(request):
    force_refresh = request.GET.get("force_refresh", "")
    grouper_name = request.GET.get("grouper", "")
    try:
        grouper = GROUPERS[grouper_name]
    except KeyError:
        grouper = GROUPERS[""]
    agg_func = calculate_agg_data
    if len(force_refresh) > 0:
        agg_func = agg_func.recache
    return partial(agg_func, grouper=grouper)


# Unfortunately, Django is incompetent to build complex queries, which is
# necessary for the goal. And also, the result data is very unlikely to change,
# so we want to cache it long enough. In case it were to change, a
# `force_refresh` flag could be passed to bypass the cache. (vide supra,
# func:`agg_func_from_request`)
@explicitly_cached(timeout=86400 * 30)
def calculate_agg_data(*, grouper: str,
                       area: Optional[str] = None, tariff: Optional[str] = None,
                       ) -> list[AggDataRow]:
    where_clause_elems = []
    if area:
        where_clause_elems.append(consumer_table.c.area == area)
    if tariff:
        where_clause_elems.append(consumer_table.c.tariff == tariff)
    if len(where_clause_elems) > 0:
        select_from = consumption_table \
            .join(consumer_table,
                  onclause=(consumer_table.c.id
                            == consumption_table.c.consumer_id))
    else:
        select_from = consumption_table

    stmt = select(
            func.strftime(grouper, consumption_table.c.datetime).label("key"),
            func.sum(consumption_table.c.amount),
            func.count(consumption_table.c.consumer_id.distinct()),
        ).select_from(select_from)
    if len(where_clause_elems) > 0:
        stmt = stmt.where(and_(*where_clause_elems))
    stmt = stmt \
        .group_by(literal_column("key")) \
        .order_by(literal_column("key"))
    compiled_sql = stmt.compile(dialect=sqlite_dialect)
    compiled_params = compiled_sql.construct_params()
    params = [compiled_params[k] for k in compiled_sql.positiontup]

    with connection.cursor() as cursor:
        cursor.execute(compiled_sql.string, params)
        return cursor.fetchall()


GROUPERS: dict[str, str] = {
    "": "%Y-%m-%d",
    "hourly-by-day": "%H",
    "monthly-by-year": "%m",
    "no": "%Y-%m-%d %H:%M:%S",
}

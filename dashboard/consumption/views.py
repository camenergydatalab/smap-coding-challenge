# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import io
import matplotlib
import matplotlib.pyplot as plt
import os
import pandas as pd
import time
from django.http import HttpResponse
from django.views.generic import ListView, DetailView

from consumption.constants import FONTNAME, SVG_PATH
from consumption.models import User, Consumption, CalculatedConsumption
from consumption.utils import plt_set_axis

matplotlib.use("agg")


class SummaryView(ListView):
    template_name = 'consumption/summary.html'
    model = User

    def render_to_response(self, context, **response_kwargs):
        start_time = time.perf_counter()

        self._delete_existing_svg(SVG_PATH)

        if not context['object_list'].count():
            return super().render_to_response(context, **response_kwargs)

        df_monthly = self._create_df_monthly()
        df_daily = self._create_df_daily()

        fig, axes = plt.subplots(nrows=1, ncols=2, tight_layout=True)
        ax1 = df_monthly.plot(ax=axes[0])
        ax2 = df_daily.plot(ax=axes[1])
        ax1.set_title(f"全消費者の月ごとの消費量", fontname=FONTNAME)
        ax2.set_title("全消費者の12月の消費量", fontname=FONTNAME)
        plt_set_axis(ax1, ax2)
        plt.savefig(SVG_PATH)

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(elapsed_time)
        return super().render_to_response(context, **response_kwargs)

    def _delete_existing_svg(self, svg_path):
        if os.path.isfile(svg_path):
            os.remove(svg_path)

    def _create_df_monthly(self):
        df = pd.DataFrame(list(CalculatedConsumption.objects.all().values('date', 'sum')))
        df['date'] = pd.to_datetime(df['date'])
        df_index = df.set_index(['date'])
        return df_index.resample('M').sum()

    def _create_df_daily(self):
        december = datetime.date(2016, 12, 1)
        df = pd.DataFrame(list(CalculatedConsumption.objects.filter(date__gte=december).values('date', 'sum')))
        return df.set_index(['date'])


class SummaryDetail(DetailView):
    template_name = 'consumption/detail.html'
    model = User

    def render_to_response(self, context, **response_kwargs):
        start_time = time.perf_counter()

        user = context.get('object')
        df_monthly = self._create_df_monthly(user)
        df_daily = self._create_df_daily(user)

        fig, axes = plt.subplots(nrows=1, ncols=2, tight_layout=True)
        ax1 = df_monthly.plot(ax=axes[0])
        ax2 = df_daily.plot(ax=axes[1])
        ax1.set_title(f"月ごとの消費量(area:{user.area} tariff:{user.tariff})", fontname=FONTNAME)
        ax2.set_title("12月の消費量", fontname=FONTNAME)
        plt_set_axis(ax1, ax2)

        buf = io.BytesIO()
        plt.savefig(buf, format='svg', bbox_inches='tight')
        svg_file = buf.getvalue()
        buf.close()
        plt.cla()

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(elapsed_time)
        return HttpResponse(svg_file, content_type='image/svg+xml')

    def _create_df_monthly(self, user):
        df = pd.DataFrame(
            list(Consumption.objects.filter(user=user).values('datetime', 'consumption')))
        df_index = df.set_index(['datetime'])
        return df_index.resample('M').sum()

    def _create_df_daily(self, user):
        december = datetime.datetime(2016, 12, 1)
        df = pd.DataFrame(
            list(Consumption.objects.filter(user=user, datetime__gte=december).values('datetime', 'consumption'))
        )
        df_index = df.set_index(['datetime'])
        return df_index.resample('D').sum()

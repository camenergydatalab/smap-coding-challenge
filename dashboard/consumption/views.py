# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import pandas as pd

from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import UserReport, ConsumptionData

# Create your views here.


class SummaryView(ListView):
    template_name = "consumption/summary.html"
    model = UserReport

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subject_name"] = "Consumption"
        context["total_consumption_label"] = "total consumption"

        data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
        data_path = os.path.join(data_dir, "consumption", "all.csv")
        df = pd.read_csv(data_path, index_col="datetime")
        chart_x = df.index.astype(str).tolist()
        chart_y = df["consumption"].tolist()
        context["chart_labels"] = chart_x
        context["chart_data"] = chart_y
        return context


class UserDetailView(DetailView):
    template_name = "consumption/detail.html"
    model = UserReport

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context["consumption_label"] = "consumption_data"

        pk = os.path.basename(self.request.path)
        print(pk)
        user_id = self.model.objects.get(pk=pk)
        print(user_id)
        data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
        data_path = os.path.join(data_dir, "consumption", f"{user_id}.csv")
        df = pd.read_csv(data_path, index_col="datetime")
        chart_x = df.index.astype(str).tolist()
        chart_y = df["consumption"].tolist()
        context["chart_labels"] = chart_x
        context["chart_data"] = chart_y

        return context

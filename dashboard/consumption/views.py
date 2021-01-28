# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
# Create your views here.
import pandas as pd



def summary(request):
    agg_df = pd.read_csv("../data/summary.csv",index_col=0)
    summary_by_area = pd.read_csv("../data/summary_area.csv")
    user_df = pd.read_csv("../data/user_data.csv")
    context = {
        "data":agg_df.to_dict(orient='list'),
        "area_data":summary_by_area.to_dict(orient="list"),
        "user_data":user_df.to_dict(orient='records')
    }
    return render(request, 'consumption/summary.html', context)


def detail(request,user_id):
    user_df = pd.read_csv("../data/consumption/"+str(user_id)+ ".csv")
    user_data_df = pd.read_csv("../data/user_data.csv")
    d = user_data_df[user_data_df["id"].isin([user_id])]
    context = {
        "user_comsumption_data":user_df.to_dict(orient="list"),
        "user_data":d.to_dict(orient="record")[0]
    }
    return render(request, 'consumption/detail.html', context)

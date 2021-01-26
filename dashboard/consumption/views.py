# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
# Create your views here.
import pandas as pd
import seaborn as sns
from pandas.core.frame import DataFrame
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import time
def summary(request):
    print(time.time())
    agg_df = pd.read_csv("../data/summary.csv",index_col=0)
    print(time.time())
    print(agg_df)
    x = agg_df["datetime"]
    y = agg_df["average"]
    print(time.time())
    # byte = BytesIO()
    # sns.lineplot(x=x,y=y)
    # plt.savefig(byte)
    # print(time.time())
    # graph = img_format(byte)
    # print(time.time())
    print(agg_df)
    user_df = pd.read_csv("../data/user_data.csv")
    context = {
        'message': 'Hello!',
        # "graph":graph,
        "data":agg_df.to_dict(orient='list'),
        "user_data":user_df.to_dict(orient='records')
    }
    return render(request, 'consumption/summary.html', context)


def detail(request):
    context = {
    }
    return render(request, 'consumption/detail.html', context)

def img_format(byte):
    byte = base64.b64encode(byte.getvalue()).decode("utf-8") 
    img = "data:image/png;base64,{}".format(byte)
    return img
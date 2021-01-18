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

def summary(request):
    
    agg_df = pd.read_csv("../data/concat.csv")
    x = agg_df["datetime"]
    y = agg_df["average"]
    byte = BytesIO()
    sns.jointplot(x, y)
    plt.savefig(byte)
    graph = img_format(byte)
    context = {
        'message': 'Hello!',
        "graph":graph
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
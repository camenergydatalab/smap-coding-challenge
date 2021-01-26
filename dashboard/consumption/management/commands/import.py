from django.core.management.base import BaseCommand
from numpy.lib.function_base import copy
import pandas as pd
import glob
import seaborn as sns
from pandas.core.frame import DataFrame
import matplotlib.pyplot as plt
import base64
from io import BytesIO

class Command(BaseCommand):
    help = 'import data'

    def handle(self, *args, **options):
        print("Implement me!")
        consumption_data_paths = glob.glob("../data/consumption/*")
        df_list = []
        agg_df = self.read_consumption_data(consumption_data_paths[0])
        for consumption_data_path in consumption_data_paths:
            df = self.read_consumption_data(consumption_data_path)
            df_list.append(df)
        agg_df = self.aggregation(df_list)
        # df = self.read_consumption_data(consumption_data_paths[1])
        # agg_df = self.aggregation(agg_df, df)
        # df = self.read_consumption_data(consumption_data_paths[2])
        # agg_df = self.aggregation(agg_df, df)
        # agg_df.drop_duplicates()
        agg_df.to_csv("../data/concat.csv")
        agg_df["average"] = agg_df.mean(axis=1)
        agg_df["total"] = agg_df.sum(axis=1)
        sum_df = agg_df[["datetime", "average", "total"]]
        sum_df.to_csv("../data/summary.csv") 
        
    def aggregation(self,df_list):
        base_df = df_list[0]
        agg_df = pd.concat(df_list,axis=1)
        agg_df = agg_df.drop_duplicates(subset=None,keep="first")
        agg_df = agg_df.drop("datetime", axis=1)
        print(agg_df)
        agg_df = pd.concat([base_df,agg_df], axis=1)
        agg_df = agg_df.drop_duplicates(subset=None,keep="first")
        print(agg_df)
        
        return agg_df

    # def aggregation(self,df_list):
    #     agg_df = df_list[0]
    #     # for df in df_list:
    #     #     print(df)
    #     #     agg_df = agg_df.merge(df, on="DateTime",copy=False)
    #     #     agg_df.dropna()
    #     #     print(agg_df.info())
    #     #     print(agg_df.describe())
    #     agg_df = agg_df.merge(df_list[1])
    #     agg_df = agg_df.merge(df_list[2])
    #     agg_df = agg_df.merge(df_list[3])
    #     agg_df = agg_df.merge(df_list[4])
    #     # agg_df = agg_df.merge(df_list[5])
    #     # agg_df = agg_df.merge(df_list[6])
    #     # agg_df = agg_df.merge(df_list[7])
    #     # agg_df = agg_df.merge(df_list[8])
    #     # agg_df = agg_df.merge(df_list[9])
    #     # agg_df = agg_df.merge(df_list[10])
    #     # agg_df = agg_df.merge(df_list[11])
    #     # agg_df = agg_df.merge(df_list[12])
    #     # agg_df = agg_df.merge(df_list[13])
    #     # agg_df = agg_df.merge(df_list[14])
    #     # agg_df = agg_df.merge(df_list[15])
    #     # agg_df = agg_df.merge(df_list[16])
    #     # agg_df = agg_df.merge(df_list[17])
    #     # agg_df = agg_df.merge(df_list[18])
    #     # agg_df = agg_df.merge(df_list[19])
    #     # agg_df = agg_df.merge(df_list[20])
    #     # agg_df = agg_df.merge(df_list[21])
    #     print(agg_df)
    #     return agg_df

    def read_user_data(self):
        user_df = pd.read_csv("../data/user_data.csv")
        pass

    def read_consumption_data(self, path):
        user_id = path.split("/")[-1].split(".")[0]
        df = pd.read_csv(path)
        new_df = df.rename(columns={"consumption":user_id})
        pd.to_datetime(new_df["datetime"].astype(str),format="%Y-%m-%d %H:%M:%S")
        print(new_df)
        return new_df



from django.core.management.base import BaseCommand
from numpy.lib.function_base import copy
import pandas as pd
import glob
from pandas.core.frame import DataFrame

class Command(BaseCommand):
    help = 'import data'

    def handle(self, *args, **options):
        self.create_summary()
        self.create_summary_by_area()
        return
    
    def create_summary(self):
        consumption_data_paths = glob.glob("../data/consumption/*")
        df_list = []
        agg_df = self.read_consumption_data(consumption_data_paths[0])
        for consumption_data_path in consumption_data_paths:
            df = self.read_consumption_data(consumption_data_path)
            df_list.append(df)
        agg_df = self.aggregation(df_list)
        
        sum_df = pd.DataFrame()
        agg_df.to_csv("../data/concat.csv")
        sum_df["datetime"] = agg_df["datetime"]
        sum_df["total"] = agg_df.sum(axis=1)
        sum_df.to_csv("../data/summary.csv")
        return

    def create_summary_by_area(self):
        user_df = pd.read_csv("../data/user_data.csv")
        grouped = user_df.groupby("area").count()
        areas_df_list = []
        for a in grouped.index.values:
            user_list_by_area = user_df[user_df["area"].isin([a])]
            area_df_list = []
            for user in user_list_by_area["id"].tolist():
                df = self.read_consumption_data("../data/consumption/"+ str(user) + ".csv")
                area_df_list.append(df)
            area_df = self.aggregation(area_df_list)
            area_sum_df = pd.DataFrame()
            area_sum_df["datetime"] = area_df["datetime"]
            area_sum_df[a] = area_df.sum(axis=1)
            areas_df_list.append(area_sum_df)
        areas_df = self.aggregation(areas_df_list)
        
        areas_df = areas_df.drop_duplicates()
        areas_df.to_csv("../data/summary_area.csv")

        return
        
    def aggregation(self,df_list):
        base_df = df_list[0].drop(df_list[0].columns[[1]], axis=1)
        agg_df = pd.concat(df_list,axis=1)
        agg_df = agg_df.drop_duplicates(subset=None,keep="first")
        agg_df = agg_df.drop("datetime", axis=1)
        agg_df = pd.concat([base_df,agg_df], axis=1)
        agg_df = agg_df.drop_duplicates(subset=None,keep="first")
        return agg_df


    def read_consumption_data(self, path):
        user_id = path.split("/")[-1].split(".")[0]
        df = pd.read_csv(path)
        new_df = df.rename(columns={"consumption":user_id})
        pd.to_datetime(new_df["datetime"].astype(str),format="%Y-%m-%d %H:%M:%S")
        return new_df



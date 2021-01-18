from django.core.management.base import BaseCommand
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
        print(consumption_data_paths)
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
        agg_df["average"] = agg_df.mean(axis=1)
        agg_df["total"] = agg_df.sum(axis=1)
        agg_df.to_csv("../data/concat.csv")
        
    def aggregation(self,df_list):
        agg_df = pd.concat(df_list,axis=1).drop_duplicates()
        print(agg_df)
        return agg_df

    def read_user_data(self):
        user_df = pd.read_csv("../data/user_data.csv")
        pass

    def read_consumption_data(self, path):
        user_id = path.split("/")[-1].split(".")[0]
        df = pd.read_csv(path)
        new_df = df.rename(columns={"consumption":user_id})
        pd.to_datetime(new_df["datetime"])
        print(new_df)
        return new_df



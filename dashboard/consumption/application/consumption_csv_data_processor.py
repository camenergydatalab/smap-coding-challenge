# -*- coding: utf-8 -*-

import os

import pandas as pd


class ConsumptionCSVDataProcessor:
    def __init__(self, csv_dir="", preprocessed_csv_dir=""):
        self.csv_dir = csv_dir
        self.preprocessed_csv_dir = preprocessed_csv_dir

    def __load(self):
        pass

    def __deduplicate(self):
        pass

    def __complete_missing_datetimes(self):
        pass

    def exec(self):
        csv_files = os.listdir(self.csv_dir)

        for file_name in csv_files:
            file_path = os.path.join(self.csv_dir, file_name)

            if os.path.isfile(file_path):
                df = pd.read_csv(file_path)

                # 重複を取り除く
                df = df.drop_duplicates(subset="datetime")

                df["datetime"] = pd.to_datetime(df["datetime"])
                df = df.set_index("datetime")

                # datetime列を30分置きに補完する
                # consumption列にNaNがある場合、一つ前のレコードの値で補完する
                df = df.asfreq("30T", method="ffill")

                preprocessed_file_path = os.path.join(
                    self.preprocessed_csv_dir, file_name
                )

                df.to_csv(preprocessed_file_path)

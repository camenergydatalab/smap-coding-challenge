# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import os
import sys

import pandas as pd
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.utils import timezone

from ...application.consumption_csv_data_processor import \
    ConsumptionCSVDataProcessor
from ...config import (CONSUMPTION_DIR, PREPROCESSED_CONSUMPTION_DIR,
                       USER_DATA_FILE)
from ...forms import ConsumptionForm, UserForm
from ...init_datas import AREAS, TARIFFS
from ...models import Area, Consumption, Tariff, User
from ...repository.consumption_repository import ConsumptionRepository
from ...repository.user_repository import UserRepository


class Command(BaseCommand):
    help = "import data"

    def init(self):
        """初期化"""
        print("=== 初期化 開始 ===")
        Consumption.objects.all().delete()
        User.objects.all().delete()
        Area.objects.all().delete()
        Tariff.objects.all().delete()

        self.areas = {}

        for area in AREAS:
            area_model = Area.objects.create(name=area[1])
            self.areas[area_model.name] = area_model

        self.tariffs = {}

        for tariff in TARIFFS:
            tariff_model = Tariff.objects.create(plan=tariff[1])
            self.tariffs[tariff_model.plan] = tariff_model

        print("=== 初期化 終了 ===")

    def preprocess_consumption_data(self):
        """消費データの前処理を行う"""
        print("=== 消費データの前処理 開始 ===")
        processor = ConsumptionCSVDataProcessor(
            CONSUMPTION_DIR, PREPROCESSED_CONSUMPTION_DIR
        )
        processor.exec()
        print("=== 消費データの前処理 終了 ===")

    def validate_user_data(self):
        """ユーザデータの入力チェック"""
        print("=== ユーザデータの入力チェック 開始 ===")

        self.users = []
        error_flag = False

        with open(USER_DATA_FILE, newline="", encoding="utf-8") as csvfile:
            count = 2

            reader = csv.DictReader(csvfile)
            for row in reader:
                area = self.areas.get(row["area"])
                area_id = None

                if area:
                    area_id = area.id

                tariff = self.tariffs.get(row["tariff"])
                tariff_id = None

                if tariff:
                    tariff_id = tariff.id

                form = UserForm(
                    {
                        "id": row["id"],
                        "area": area_id,
                        "tariff": tariff_id,
                    }
                )

                if form.is_valid():
                    self.users.append(
                        User(
                            id=form.cleaned_data["id"],
                            area=form.cleaned_data["area"],
                            tariff=form.cleaned_data["tariff"],
                        )
                    )
                else:
                    error_flag = True
                    print(f"{count}行目にエラー発生")
                    for key in form.errors:
                        message = form.errors[key].as_text()
                        print(f"{key} : {message}")

                count += 1

        print("=== ユーザデータの入力チェック 終了 ===")

        if error_flag:
            sys.exit()

    def validate_consumption_data(self):
        """消費データの入力チェック"""
        print("=== 消費データの入力チェック 開始 ===")

        error_flag = False

        preprocessed_csv_files = os.listdir(PREPROCESSED_CONSUMPTION_DIR)

        for file_name in preprocessed_csv_files:

            if file_name == 'empty':
                continue

            file_path = os.path.join(PREPROCESSED_CONSUMPTION_DIR, file_name)

            with open(file_path, newline="", encoding="utf-8") as csvfile:
                count = 2

                reader = csv.DictReader(csvfile)

                for row in reader:
                    form = ConsumptionForm(
                        {
                            "datetime": row["datetime"],
                            "value": row["consumption"],
                        }
                    )

                    if not form.is_valid():
                        error_flag = True
                        print(f"{file_name} {count}行目にエラー発生")
                        for key in form.errors:
                            message = form.errors[key].as_text()
                            print(f"{key} : {message}")

                    count += 1

        print("=== 消費データの入力チェック 終了 ===")

        if error_flag:
            sys.exit()

    def bulk_insert_user(self):
        """ユーザデータに対して、バルクインサートを行う"""
        print("=== ユーザデータ バルクインサート 開始 ===")
        UserRepository.bulk_insert(self.users)
        print("=== ユーザデータ バルクインサート 終了 ===")

    def bulk_insert_consumption_data(self):
        """消費データに対して、1000件でバルクインサートを行う"""
        print("=== 消費データ バルクインサート 開始 ===")
        for user in UserRepository.get_all():
            file_path = os.path.join(PREPROCESSED_CONSUMPTION_DIR, str(user) + ".csv")
            chunked_df = pd.read_csv(file_path, chunksize=1000)

            for df in chunked_df:
                consumption_datas = []

                df["datetime"] = pd.to_datetime(df["datetime"])

                for index, row in df.iterrows():
                    consumption_datas.append(
                        Consumption(
                            user=user,
                            datetime=timezone.make_aware(row["datetime"]),
                            value=row["consumption"],
                        )
                    )

                ConsumptionRepository.bulk_insert(consumption_datas)
        print("=== 消費データ バルクインサート 終了 ===")

    def delete_preprocess_consumption_csv_file(self):
        """前処理を施した消費CSVファイルの削除"""
        preprocessed_csv_files = os.listdir(PREPROCESSED_CONSUMPTION_DIR)

        for file_name in preprocessed_csv_files:

            if file_name == 'empty':
                continue

            file_path = os.path.join(PREPROCESSED_CONSUMPTION_DIR, file_name)
            os.remove(file_path)

    def handle(self, *args, **options):
        #self.init()

        #self.preprocess_consumption_data()

        #self.validate_user_data()

        #self.validate_consumption_data()

        #try:
        #    self.bulk_insert_user()
        #except IntegrityError:
        #    print("ユーザ登録にて、ユニーク制約違反が発生しました。")
        #    sys.exit()

        #try:
        #    self.bulk_insert_consumption_data()
        #except IntegrityError:
        #    print("消費データにて、ユニーク制約違反が発生しました。")
        #    sys.exit()

        self.delete_preprocess_consumption_csv_file()

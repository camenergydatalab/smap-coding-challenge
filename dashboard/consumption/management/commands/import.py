import logging
import glob
import shutil
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from pathlib import Path
import pandas as pd
import os
from consumption.models.master import Area, TariffPlan
from consumption.models.user_related import User, UserConsumptionHistory, UserContractHistory
from consumption.utils.time_utils import get_local_now_time
from django_pandas.io import read_frame
from consumption.models.user_related import User, UserConsumptionHistory, UserContractHistory
from django.core.cache import cache
import jpholiday
import datetime
from django_pandas.io import read_frame
from consumption.consts import CONSUMPTION_CACHE_KEY


class Command(BaseCommand):
    help = 'Import data from CSV to DB'

    DATA_FILE_PATH = f'{Path(settings.BASE_DIR).parent}/data'
    AREA_DICT = Area.get_area_dict()
    TARIFF_PLAN_DICT = TariffPlan.get_tariff_plan_dict()
    IMPORTED_FILE_PATH = f"{DATA_FILE_PATH}/completion/{get_local_now_time().date()}"

    @transaction.atomic
    def import_user_data(self):
        logging.info("import_user_data has started.")

        user_data_file = f'{self.DATA_FILE_PATH}/user_data.csv'

        # ファイルが存在しなかったら処理しない
        if not os.path.exists(user_data_file):
            logging.info("user_data.csv does not existed.")
            return

        df = pd.read_csv(user_data_file)

        # DBには登録されているが、CSVファイルに存在しないユーザはステータスを退会に変更する
        users_exclude_withdrawn = User.objects.exclude(user_status=User.USER_STATUS.withdrawn)
        user_db_df = read_frame(users_exclude_withdrawn, fieldnames=["user_id"])
        # ~df.isinで含まない行のみ取得する
        withdrawn_user_df = user_db_df[~user_db_df["user_id"].isin(df["id"].astype(str))]
        if len(withdrawn_user_df) > 0:
            withdrawn_users = users_exclude_withdrawn.filter(user_id__in=withdrawn_user_df["user_id"])
            withdrawn_user_list = []
            for withdrawn_user in withdrawn_users:
                withdrawn_user.user_status = User.USER_STATUS.withdrawn
                withdrawn_user_list.append(withdrawn_user)
            User.objects.bulk_update(withdrawn_user, fields=["user_status"])
            logging.info(f"user_ids {list(withdrawn_user_df['user_id'])} have withdrawn.")

        update_user_list = []
        new_user_contract_history_list = []
        update_user_contract_history_list = []
        for index, row in df.iterrows():
            # ユーザID、エリア、料金プランの値が存在しない場合後続処理を行わない
            # TODO 行ごとでなくても全体で存在しない値がある行を削除する処理に変更でも行けそう
            if row.isnull().any():
                logging.info(f"row={index+2} : all values are not complete. Skipping processing.")
                continue

            user_id = row["id"]
            area = Area.get_area_dict().get(row["area"])
            tariff_plan = TariffPlan.get_tariff_plan_dict().get(row["tariff"])

            # エリア、料金プランのマスタテーブルに存在しない値の場合処理を行わない
            if not area or not tariff_plan:
                logging.info(f"user_id {user_id} : area or tariff_plan mismatch. Skipping processing.")
                continue

            user, created = User.objects.get_or_create(user_id=user_id)
            # ユーザのステータスが退会済みになっていたら継続に戻す
            if user.user_status == User.USER_STATUS.withdrawn:
                user.user_status = User.USER_STATUS.continuing
                update_user_list.append(user)
                logging.info(f"user_id {user_id} status change to 'continuing")

            if created:
                # DBに登録されていないユーザの場合、新規登録処理を行う
                self.append_new_user_contract_history_list(
                    user, area, tariff_plan, new_user_contract_history_list
                )
                logging.info(f"user_id {user_id} is new_create_user.")
            elif not UserContractHistory.objects.filter(user=user, area=area, tariff_plan=tariff_plan).exists():
                # ユーザID、エリア、料金プランが履歴テーブルに存在しない場合、更新処理を行う
                self.append_update_user_contract_history_list(user, update_user_contract_history_list)
                self.append_new_user_contract_history_list(
                    user, area, tariff_plan, new_user_contract_history_list
                )
                logging.info(f"user_id {user_id} is update_user.")
            else:
                # 上記に合致しないユーザの場合処理しない
                logging.info(f"user_id {user_id} has no changes")
                continue

        UserContractHistory.objects.bulk_create(new_user_contract_history_list)
        UserContractHistory.objects.bulk_update(update_user_contract_history_list, fields=["contract_end_at"])
        os.makedirs(self.IMPORTED_FILE_PATH, exist_ok=True)
        shutil.move(user_data_file, f"{self.IMPORTED_FILE_PATH}/user_data.csv")
        logging.info("import_user_data has finished.")


    def append_new_user_contract_history_list(self, user, area, tariff_plan, new_user_contract_history_list):
        contract_history = UserContractHistory(user=user, area=area, tariff_plan=tariff_plan)
        new_user_contract_history_list.append(contract_history)

    def append_update_user_contract_history_list(self, user, update_user_contract_history_list):
        # 最新の契約履歴データに契約終了日を本日日付で格納する
        last_contract_history = UserContractHistory.objects.filter(user=user).last()
        last_contract_history.contract_end_at = get_local_now_time()
        update_user_contract_history_list.append(last_contract_history)

    @transaction.atomic
    def import_consumption_data(self):
        # TODO 削除処理消すの忘れない
        UserConsumptionHistory.objects.all().delete()
        logging.info("import_consumption_data has started.")
        consumption_csv_files = glob.glob(f"{self.DATA_FILE_PATH}/consumption/*.csv")
        # ファイルが存在しなかったら処理しない
        if not consumption_csv_files:
            logging.info("consumption_csv_file does not existed.")
            return

        # 消費量CSVを1ファイルごと（ユーザごと）処理する
        create_user_consumptionHistory_list = []
        for user_consumption_csv_file in consumption_csv_files:
            user_id = os.path.basename(user_consumption_csv_file).split('.')[0]
            logging.info(f"user_id {user_id} : import consumption has started.")
            df = pd.read_csv(user_consumption_csv_file)
            user = User.objects.filter(user_id=user_id).last()

            # 未登録ユーザの場合処理しない
            if not user:
                logging.info(f"{user_id} : User does not found. Skipping processing")
                continue

            # 一括登録できるようにCSVのヘッダーをモデルのフィールド名に直す
            df = df.rename(columns={'datetime': 'measurement_at','consumption': "consumption_amount"})
            df.insert(0, "user", user)
            df = df.drop_duplicates(subset='measurement_at')
            df['measurement_at'] = pd.to_datetime(df['measurement_at']).dt.tz_localize(settings.TIME_ZONE)

            user_consumption_history = UserConsumptionHistory.objects.filter(user__user_id=user_id)
            # 対象ユーザの消費履歴が存在する場合、格納されていないデータのみ抽出する
            if user_consumption_history:
                db_df = read_frame(user_consumption_history, fieldnames=['measurement_at'])
                consumption_datetime_df_from_db = db_df['measurement_at'].dt.tz_convert(settings.TIME_ZONE)
                df = df[~df["measurement_at"].isin(consumption_datetime_df_from_db)]
            records = df.to_dict("records")
            create_user_consumptionHistory_list.extend(records)

        #TODO 現状以下の登録処理にて30秒近くかかっているが、改善できる？
        UserConsumptionHistory.objects.bulk_create(
            [UserConsumptionHistory(**data) for data in create_user_consumptionHistory_list]
        )
        shutil.move(f"{self.DATA_FILE_PATH}/consumption", f"{self.DATA_FILE_PATH}/completion/{get_local_now_time().date()}")

    def cache_summary_data(self):
        # TODO 本来であれば本日から1か月前までを対象期間とするが、データの関係上1か月間の期間はハードコーディングする
        start_date=datetime.date(2016, 12, 1)
        end_date=datetime.date(2016, 12, 31)

        # User関連データを連結したデータフレームを作成する
        user_data = User.objects.values('user_id').filter()
        consumption_history_data = UserConsumptionHistory.objects.values('user__user_id', 'measurement_at', 'consumption_amount').filter(measurement_at__range=(start_date, end_date))
        contract_history_data = UserContractHistory.objects.values('user__user_id', "area__area_name", "tariff_plan","contract_start_at", "contract_end_at")
        user_df = read_frame(user_data)
        consumption_history_df = read_frame(consumption_history_data)
        contract_history_df = read_frame(contract_history_data)
        merged_df = pd.merge(contract_history_df, user_df, left_on='user__user_id', right_on='user_id')
        merged_df = pd.merge(merged_df, consumption_history_df, on='user__user_id')
        consumption_result_df = merged_df[['user_id', 'area__area_name', 'tariff_plan',"contract_start_at", "contract_end_at", 'measurement_at', 'consumption_amount']]
        consumption_result_df['measurement_at'] = consumption_result_df['measurement_at'].dt.tz_convert(settings.TIME_ZONE)

        # 平日か休日(祝日含む)か判定
        holidays = [date[0] for date in jpholiday.between(start_date, end_date)]
        consumption_result_df['is_holiday'] = (consumption_result_df['measurement_at'].dt.dayofweek >= 5) | (consumption_result_df['measurement_at'].isin(holidays))

        # 時間帯判別処理
        # 深夜（0:00~5:00）、 朝（05:00~10:00）, 昼（10:00~15:00）, 夕方（15:00~19:00）, 夜（19:00~24:00）
        bins = [-1, 5, 10, 15, 19, 25]
        labels = ['late_night', 'morning', 'daytime', 'evening', 'night']
        consumption_result_df['time_of_day'] = pd.cut(consumption_result_df['measurement_at'].dt.hour, bins=bins, labels=labels, right=False)
        cache.set(CONSUMPTION_CACHE_KEY, consumption_result_df, timeout=60*60)


    def handle(self, *args, **options) -> str:
        try:
            self.import_user_data()
            self.import_consumption_data()
            self.cache_summary_data()
            return "0"
        except Exception as e:
            logging.error(e)
            return "1"
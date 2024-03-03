from django.core.management.base import BaseCommand
from django.db import transaction
import logging
from django.conf import settings
from pathlib import Path
import pandas as pd
import os
from consumption.models.master import Area, TariffPlan
from consumption.models.user_related import User, UserContractHistory
from consumption.utils.time_utils import get_local_time

class Command(BaseCommand):
    help = 'Import data from CSV to DB'

    DATA_FILE_PATH = f'{Path(settings.BASE_DIR).parent}/data'
    AREA_DICT = Area.get_area_dict()
    TARIFF_PLAN_DICT = TariffPlan.get_tariff_plan_dict()

    @transaction.atomic
    def import_user_data(self):
        logging.info("import_user_data has started.")

        user_data_file = f'{self.DATA_FILE_PATH}/user_data.csv'
        df = pd.read_csv(user_data_file)

        # ファイルが存在しなかったら処理しない
        if not os.path.exists(user_data_file):
            logging.info("user_data.csv has not existed.")
            return

        # DBには登録されているが、CSVファイルに存在しないユーザはステータスを退会に変更する
        user_ids_set_from_csv = set(df["id"].dropna())
        user_ids_set_from_db = set(User.objects.values_list('user_id', flat=True))
        withdrawn_user_ids_set = user_ids_set_from_db - user_ids_set_from_csv
        User.objects.filter(user_id__in=withdrawn_user_ids_set).update(user_status=User.USER_STATUS.withdrawn)
        logging.info(f"{withdrawn_user_ids_set} have withdrawn.")

        new_user_contract_history_list = []
        update_user_contract_history_list = []
        for index, row in df.iterrows():
            # ユーザID、エリア、料金プランの値が存在しない場合後続処理を行わない
            if row.isnull().any():
                logging.info(f"row={index+2} has not registered because all values are not complete.")
                continue

            user_id = row["id"]
            area = self.AREA_DICT.get(row["area"])
            tariff_plan = self.TARIFF_PLAN_DICT.get(row["tariff"])
            # エリア、料金プランのマスタテーブルに存在しない値の場合処理を行わない
            if not area or not tariff_plan:
                logging.info(f"{user_id} has not registered because area or tariff_plan mismatch.")
                continue

            user, created = User.objects.get_or_create(user_id=user_id)
            if created:
                # DBに登録されていないユーザの場合、新規登録処理を行う
                self.append_new_user_contract_history_list(user, area, tariff_plan, new_user_contract_history_list)
                logging.info(f"{user_id} has created.")
            elif not UserContractHistory.objects.filter(user=user, area=area, tariff_plan=tariff_plan).exists():
                # ユーザID、エリア、料金プランが履歴テーブルに存在しない場合、更新処理を行う
                self. append_update_user_contract_history_list(user, update_user_contract_history_list)
                self.append_new_user_contract_history_list(user, area, tariff_plan, new_user_contract_history_list)
                logging.info(f"{user_id} has updated.")
            else:
                # 上記に合致しないユーザの場合処理しない
                logging.info(f"{user_id} has no changes")
                continue

        UserContractHistory.objects.bulk_create(new_user_contract_history_list)
        UserContractHistory.objects.bulk_update(update_user_contract_history_list, fields=["contract_end_at"])

        logging.info("import_user_data has finished.")


    def append_new_user_contract_history_list(self, user, area, tariff_plan, new_user_contract_history_list):
        contract_history = UserContractHistory(user=user, area=area, tariff_plan=tariff_plan)
        new_user_contract_history_list.append(contract_history)


    def append_update_user_contract_history_list(self, user, update_user_contract_history_list):
        # 最新の契約履歴データに契約終了日を本日日付で格納する
        last_contract_history = UserContractHistory.objects.filter(user=user).last()
        last_contract_history.contract_end_at = get_local_time()
        update_user_contract_history_list.append(last_contract_history)


    def handle(self, *args, **options) -> str:
        try:
            self.import_user_data()
            return "0"
        except Exception as e:
            logging.error(e)
            return "1"
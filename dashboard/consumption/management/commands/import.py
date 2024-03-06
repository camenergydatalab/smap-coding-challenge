import glob
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from consumption.models.master import Area, TariffPlan
from consumption.models.user_related import User, UserConsumptionHistory, UserContractHistory
from consumption.utils.cache_utils import cache_consumption_data
from consumption.utils.time_utils import get_local_now_time
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import IntegrityError
from django_pandas.io import read_frame


class Command(BaseCommand):
    help = "Import data from CSV to DB"

    DATA_FILE_PATH = f"{Path(settings.BASE_DIR).parent}/data"
    IMPORTED_FILE_PATH = f"{DATA_FILE_PATH}/completion/{get_local_now_time().date()}"

    @transaction.atomic
    def import_user_data(self) -> None:
        """ユーザデータのインポート処理
        Note:
            local環境での動作確認時には、ファイル移動処理はコメントアウトしておく方が楽です
        """
        logging.info("import_user_data has started.")

        # ファイルが存在しなかったら処理しない
        user_data_file = f"{self.DATA_FILE_PATH}/user_data.csv"
        if not os.path.exists(user_data_file):
            logging.info("user_data.csv does not existed.")
            return

        # 欠陥値とユーザIDの重複を排除したdata_frameを取得する
        user_data_df = self.create_df_except_nan_and_duplicates(user_data_file, ["id"])
        # ユーザの分類ごと（登録、更新）のリストを作成する
        (
            update_user_list,
            create_user_contract_history_list,
            update_user_contract_history_list,
        ) = self.create_lists_each_user_categories(user_data_df)
        # 退会ユーザのステータスを変更する
        self.change_user_status_withdrawn(user_data_df, update_user_list)

        # データの登録処理
        try:
            User.objects.bulk_update(update_user_list, fields=["user_status"])
            UserContractHistory.objects.bulk_create(create_user_contract_history_list)
            UserContractHistory.objects.bulk_update(update_user_contract_history_list, fields=["contract_end_at"])
        except IntegrityError as e:
            logging.error(f"Error in bulk_update/create: {e}")
            raise

        # 実施後、ファイルを完了フォルダに移動する。
        try:
            self.makedir_and_movefile(user_data_file, f"{self.IMPORTED_FILE_PATH}/user_data.csv")
        except OSError as e:
            logging.info(f"Error in makedir or movefile: {e}")
            raise

        logging.info("import_user_data has finished.")

    def makedir_and_movefile(self, before_path: str, after_path: str) -> None:
        """処理済ファイルの移動処理
        Args:
            before_path: 移動前のパス
            after_path: 移動後のパス
        Todo:
            正常終了したファイルのみ移動する処理への変更
        """
        os.makedirs(self.IMPORTED_FILE_PATH, exist_ok=True)
        shutil.move(before_path, after_path)

    def change_user_status_withdrawn(self, user_data_df: pd.DataFrame, update_user_list: List[User]) -> None:
        """退会ユーザのステータス変更処理
        Args:
            user_data_df: user_data.csvを読み込んだデータフレーム
            update_user_list: ステータス更新するユーザのリスト

        Note:
            DBに登録されている(退会済み以外)が、CSVファイルに存在しないユーザはステータスを退会に変更する
        """
        users_exclude_withdrawn = User.objects.exclude(user_status=User.USER_STATUS.withdrawn)
        user_db_df = read_frame(users_exclude_withdrawn, fieldnames=["user_id"])
        # ~df.isinで含まない行のみ取得する
        withdrawn_user_df = user_db_df[~user_db_df["user_id"].isin(user_data_df["id"].astype(str))]
        if len(withdrawn_user_df) > 0:
            withdrawn_users = users_exclude_withdrawn.filter(user_id__in=withdrawn_user_df["user_id"])
            for withdrawn_user in withdrawn_users:
                withdrawn_user.user_status = User.USER_STATUS.withdrawn
                update_user_list.append(withdrawn_user)
            logging.info(f"user_ids {list(withdrawn_user_df['user_id'])} have withdrawn.")

    def create_lists_each_user_categories(
        self, user_data_df: pd.DataFrame
    ) -> Tuple[List[User], List[UserContractHistory], List[UserContractHistory]]:
        """ユーザの分類別リスト作成処理
        Args:
            user_data_df: user_data.csvを読み込んだデータフレーム

        Return:
            update_user_list: ステータス更新するユーザのリスト
            create_user_contract_history_list: 新しく作成する契約履歴データのリスト
            update_user_contract_history_list: 契約履歴を更新するデータのリスト
        """

        update_user_list = []
        create_user_contract_history_list = []
        update_user_contract_history_list = []
        for _, row in user_data_df.iterrows():
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
                self.append_create_user_contract_history_list(
                    user, area, tariff_plan, create_user_contract_history_list
                )
                logging.info(f"user_id {user_id} is new_create_user.")
            elif not UserContractHistory.objects.filter(user=user, area=area, tariff_plan=tariff_plan).exists():
                # ユーザID、エリア、料金プランが履歴テーブルに存在しない場合、更新処理を行う
                self.append_update_user_contract_history_list(user, update_user_contract_history_list)
                self.append_create_user_contract_history_list(
                    user, area, tariff_plan, create_user_contract_history_list
                )
                logging.info(f"user_id {user_id} is update_user.")
            else:
                # 上記に合致しないユーザの場合処理しない
                logging.info(f"user_id {user_id} has no changes")
                continue

        return update_user_list, create_user_contract_history_list, update_user_contract_history_list

    def create_df_except_nan_and_duplicates(self, csv_file_name: str, duplicate_columns: List[str]) -> pd.DataFrame:
        """重複データと欠陥値を削除したデータフレームを作成する処理
        Args:
            csv_file_name: データフレームを作成するCSVのファイル名
            duplicate_columns: 重複を排除するキー

        Return:
            重複データと欠陥値を削除したデータフレーム

        Todo:
            登録できなかったデータをまとめたCSVファイルの作成処理
        """
        data_df = pd.read_csv(csv_file_name)
        # ログ出力用に存在しない値がある行のみのデータフレームを作成し
        isnull_data_df = data_df[data_df.isnull().any(axis=1)]
        if len(isnull_data_df) > 0:
            logging.info(
                f"file: {csv_file_name} index: {list(isnull_data_df.index)} : all values are not complete. Skipping processing."
            )

        data_df = data_df.dropna().drop_duplicates(subset=duplicate_columns)
        return data_df

    def append_create_user_contract_history_list(
        self,
        user: User,
        area: Area,
        tariff_plan: TariffPlan,
        create_user_contract_history_list: List[UserContractHistory],
    ) -> None:
        """新規契約履歴データのリストへの追加処理
        Args:
            user: 対象ユーザ
            area: エリア
            tariff_plan: 料金プラン
            create_user_contract_history_list:  新しく作成する契約履歴データのリスト
        """
        contract_history = UserContractHistory(user=user, area=area, tariff_plan=tariff_plan)
        create_user_contract_history_list.append(contract_history)

    def append_update_user_contract_history_list(
        self, user: User, update_user_contract_history_list: List[UserContractHistory]
    ) -> None:
        """契約終了履歴データのリストへの追加
        Args:
            user: 対象ユーザ
            update_user_contract_history_list:  契約履歴を更新するデータのリスト
        Note:
            最新の契約履歴データに契約終了日を本日日付で格納する
        """
        last_contract_history = UserContractHistory.objects.filter(user=user).last()
        last_contract_history.contract_end_at = get_local_now_time()
        update_user_contract_history_list.append(last_contract_history)

    @transaction.atomic
    def import_consumption_data(self) -> None:
        """消費量データのインポート処理
        Todo:
            bulk_createに30秒近くかかっているが、調査できていない
        """
        logging.info("import_consumption_data has started.")

        # ファイルが存在しなかったら処理しない
        consumption_csv_files = glob.glob(f"{self.DATA_FILE_PATH}/consumption/*.csv")
        if not consumption_csv_files:
            logging.info("consumption_csv_file does not existed.")
            return
        user_consumption_history_list = self.create_user_consumption_history_list(consumption_csv_files)

        try:
            UserConsumptionHistory.objects.bulk_create(
                [UserConsumptionHistory(**data) for data in user_consumption_history_list]
            )
        except IntegrityError as e:
            logging.error(f"Error in bulk_create UserConsumptionHistory: {e}")
            raise

        # 実施後、ファイルを完了フォルダに移動する。
        try:
            self.makedir_and_movefile(f"{self.DATA_FILE_PATH}/consumption", self.IMPORTED_FILE_PATH)
        except OSError as e:
            logging.info(f"Error in makedir or movefile: {e}")
            raise

        logging.info("import_consumption_data has finished.")

    def create_user_consumption_history_list(self, consumption_csv_files: List[str]) -> List[Dict]:
        """全ユーザ分の消費履歴データリスト作成処理
        Args:
            consumption_csv_files: 消費量データのCSVファイル（全ユーザ分）
        Return:
            全ユーザ分の消費履歴データリスト
        """
        # 消費量CSVを1ファイルごと（ユーザごと）処理する
        user_consumption_history_list = []
        for user_consumption_csv_file in consumption_csv_files:
            user_id = os.path.basename(user_consumption_csv_file).split(".")[0]
            logging.info(f"user_id {user_id} : import consumption has started.")

            # 未登録ユーザの場合処理しない
            user = User.objects.filter(user_id=user_id).last()
            if not user:
                logging.info(f"user_id {user_id} : User does not found. Skipping processing")
                continue

            # 欠陥値と測定日時の重複を排除したdata_frameを取得する
            user_consumption_data_df = self.create_df_except_nan_and_duplicates(user_consumption_csv_file, ["datetime"])

            # データの一括登録ができるようDataFrameを調整する
            user_consumption_data_df = user_consumption_data_df.rename(
                columns={"datetime": "measurement_at", "consumption": "consumption_amount"}
            )
            user_consumption_data_df["measurement_at"] = pd.to_datetime(
                user_consumption_data_df["measurement_at"]
            ).dt.tz_localize(settings.TIME_ZONE)
            user_consumption_data_df.insert(0, "user", user)

            # まだDBに格納されていない消費履歴データのみ抽出する
            user_consumption_history = UserConsumptionHistory.objects.filter(user__user_id=user_id)
            if user_consumption_history:
                db_df = read_frame(user_consumption_history, fieldnames=["measurement_at"])
                consumption_datetime_df_from_db = db_df["measurement_at"].dt.tz_convert(settings.TIME_ZONE)
                user_consumption_data_df = user_consumption_data_df[
                    ~user_consumption_data_df["measurement_at"].isin(consumption_datetime_df_from_db)
                ]
            records = user_consumption_data_df.to_dict("records")
            user_consumption_history_list.extend(records)
        return user_consumption_history_list

    def cache_consumption_data(self):
        """画面表示で使用する消費量データのキャッシュ処理
        """
        logging.info("cache_summary_data has started.")
        cache_consumption_data()
        logging.info("cache_summary_data has finished.")


    def handle(self, *args, **options) -> str:
        try:
            self.import_user_data()
            self.import_consumption_data()
            self.cache_consumption_data()
            return "0"
        except (IntegrityError, OSError) as e:
            logging.error(e)
            return "1"

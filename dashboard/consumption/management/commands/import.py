import csv
import glob
import os

from django.core.management.base import BaseCommand

from consumption.models import UserData, ConsumptionData


class Command(BaseCommand):
    help = 'import data'

    def handle(self, *args, **options):
        # print("Implement me!")

        # user data
        user_data_file_path = options["user"]
        if user_data_file_path:
            # データ読み込み
            data = data_from_csv_file(user_data_file_path)

            # データの保存
            store_user_data(data)

        # consumption data
        # データ読み込み
        consumption_data_dir_path = options['consumption']
        if consumption_data_dir_path:
            for data_file_path in glob.glob(consumption_data_dir_path + r"\\*.csv"):
                data = data_from_csv_file(data_file_path)

                # データの保存
                file_name = os.path.basename(data_file_path)
                user_id, _ = os.path.splitext(file_name)
                store_consumption_data(user_id, data)

    def add_arguments(self, parser):
        parser.add_argument('-u', '--user', type=str)
        parser.add_argument('-c', '--consumption', type=str)


def store_user_data(data: list):
    """
    ユーザデータの保存
    :param data: list
        [{'id': str, 'area': str, 'tariff': str}, ...]
    :return: None
    """
    UserData.objects.bulk_create([UserData(**item) for item in data])


def store_consumption_data(user_id: str, data: list):
    """
    :param user_id: str
        User ID
    :param data: list
        [{"datetime": "YYYY-mm-DD HH:MM:SS", "consumption": float}]
    :return: None
    """
    ConsumptionData.objects.bulk_create([ConsumptionData(user_id=user_id, **item) for item in data])


def data_from_csv_file(file_path):
    _, ext = os.path.splitext(file_path)

    if ext != '.csv':
        raise

    with open(file_path) as f:
        reader = csv.DictReader(f)
        data = list(reader)
    return data

import csv
import glob
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware

from consumption.models import UserData, ConsumptionData


class Command(BaseCommand):
    help = "import data"

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
        consumption_data_dir_path = options["consumption"]
        if consumption_data_dir_path:
            csv_file_paths = get_csv_file_paths(consumption_data_dir_path)
            for data_file_path in csv_file_paths:
                data = data_from_csv_file(data_file_path)

                # データの保存
                user_id = Path(data_file_path).stem
                store_consumption_data(user_id, data)

    def add_arguments(self, parser):
        parser.add_argument("-u", "--user", type=str)
        parser.add_argument("-c", "--consumption", type=str)


def get_csv_file_paths(dir_path):
    return glob.glob(dir_path + r"\\*.csv")


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
    同じ日時のデータがある場合は上書きする。

    :param user_id: str
        User ID
    :param data: list
        [{"datetime": "YYYY-mm-DD HH:MM:SS", "consumption": float}]
    :return: None
    """

    map_datetime_data = {}
    for item in data:
        item["datetime"] = make_aware(
            datetime.strptime(item["datetime"], "%Y-%m-%d %H:%M:%S")
        )
        map_datetime_data[item["datetime"]] = item

    ConsumptionData.objects.bulk_create(
        [
            ConsumptionData(user_id=user_id, **item)
            for item in map_datetime_data.values()
        ]
    )


def data_from_csv_file(file_path):
    ext = Path(file_path).suffix

    if ext != ".csv":
        raise

    with open(file_path) as f:
        reader = csv.DictReader(f)
        data = list(reader)
    return data

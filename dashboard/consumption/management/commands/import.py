from django.core.management.base import BaseCommand
import os
import pandas as pd
from consumption.models import User, Consumption
from django.db import transaction
from datetime import datetime
from django.utils import timezone

class Command(BaseCommand):
    help = 'Import user and consumption data from CSV'

    def handle(self, *args, **options):
        print("Import User start!")
        user_csv_file_path = 'data/user_data.csv'

        if not os.path.isfile(user_csv_file_path):
            self.stdout.write(self.style.ERROR('User CSV file not found'))
            return

        consumption_csv_directory = 'data/consumption/'

        if not os.path.exists(consumption_csv_directory):
            self.stdout.write(self.style.ERROR('Consumption CSV directory not found'))
            return

        # すでに存在するユーザーのIDを取得
        user_ids = set(User.objects.values_list('id', flat=True))

        try:
          with transaction.atomic():
            # ユーザーデータの一括挿入
            user_df = pd.read_csv(user_csv_file_path)
            User.objects.bulk_create([
                    User(id=row['id'], area=row['area'], tariff=row['tariff'])
                    for _, row in user_df.iterrows()
                    if row['id'] not in user_ids # すでに存在するユーザーをスキップ
                ])
            self.stdout.write(self.style.SUCCESS('User data imported successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            return  # ユーザーデータ取り込みに失敗した場合、ここで終了


        print("Import Consumption start!")
        # すでに存在するユーザーのIDを取得
        user_ids = set(User.objects.values_list('id', flat=True))

        try:
          with transaction.atomic():
            # 消費データの一括挿入
            consumption_data_to_insert = []

            for csv_file_name in os.listdir(consumption_csv_directory):
                if csv_file_name.endswith('.csv'):
                    csv_file_path = os.path.join(consumption_csv_directory, csv_file_name)
                    consumption_df = pd.read_csv(csv_file_path)

                    # ファイル名からユーザーIDを取得
                    user_id = int(os.path.splitext(csv_file_name)[0])

                    # 対応するユーザーが存在しない場合はスキップ
                    if user_id not in user_ids:
                        print(user_id)
                        self.stdout.write(self.style.WARNING(f'Skipping consumption import for user_id={user_id}'))
                        continue

                    for _, row in consumption_df.iterrows():
                        datetime_str = row['datetime']
                        datetime_obj = pd.to_datetime(datetime_str, format='%Y-%m-%d %H:%M:%S')

                        # タイムゾーン情報を含める
                        datetime_obj_with_tz = timezone.make_aware(datetime_obj)

                        consumption_data_to_insert.append(
                            Consumption(datetime=datetime_obj_with_tz, consumption=row['consumption'], user_id=user_id)
                        )

            # バルクインサートを実行
            Consumption.objects.bulk_create(consumption_data_to_insert)

            self.stdout.write(self.style.SUCCESS('Consumption data imported successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

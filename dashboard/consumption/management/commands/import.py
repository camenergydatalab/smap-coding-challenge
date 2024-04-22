from django.core.management.base import BaseCommand
from ... import models
import csv
import os
import glob
from datetime import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        # ユーザーデータのインポート
        file_path = '..\\data\\user_data.csv'
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_data = csv.reader(file)
            next(csv_data)
            for row in csv_data:
                user, created = models.User.objects.get_or_create(user_id=row[0])
                user.user_id = row[0]
                user.user_area = row[1]
                user.user_tariff = row[2]
                user.save()

        # 消費データのインポート
        dir_path = "..\\data\\consumption"
        file_list = glob.glob(os.path.join(dir_path, "*.csv"))
        for file_path in file_list:
            user_id = file_path.replace(dir_path + '\\', '').replace('.csv', '')
            user = models.User.objects.get(user_id=user_id)
            with open(file_path, mode='r', encoding='utf-8') as file:
                csv_data = csv.reader(file)
                next(csv_data)
                data_list = []
                for row in csv_data:
                    consumption = models.Consumption()
                    consumption.user_id = user
                    consumption.cousumption_datetime = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
                    consumption.cousumption_value = row[1]
                    data_list.append(consumption)
                models.Consumption.objects.bulk_create(data_list)

        print('Import Success')

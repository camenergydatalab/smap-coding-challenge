import csv
import datetime
import os
from os import listdir
from os.path import isfile, join

from consumption.models import Consumption, User
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware

BASE_DIR = getattr(settings, "BASE_DIR", None)
DATA_DIR = os.path.join(BASE_DIR, '../data')
USER_DATA_FILE = 'user_data.csv'
CONSUM_DATA_DIR_NAME = 'consumption'


class Command(BaseCommand):
    def handle(self, *args, **options):
        # read user data
        user_data_file = self.get_user_data()
        self.read_user(user_data_file)

        # read consumption data
        consumption_data_file_list = self.get_consumption_data_list()
        for file in consumption_data_file_list:
            self.read_consumption(file)

    def get_user_data(self):
        return os.path.join(DATA_DIR, USER_DATA_FILE)

    def get_consumption_data_list(self):
        data_dir = os.path.join(DATA_DIR, CONSUM_DATA_DIR_NAME)

        return [
            os.path.abspath(os.path.join(data_dir, f)) for f in listdir(
                data_dir
            ) if isfile(
                join(data_dir, f)
            )
        ]

    def read_user(self, user_data_file):
        # create user data
        with open(user_data_file) as f:
            reader = csv.reader(f)
            next(reader)
            User.objects.bulk_create(
                [
                    User(
                        id=row[0],
                        area=row[1],
                        tariff=row[2],
                    ) for row in reader
                ]
            )

    def read_consumption(self, file):
        # create consunption data
        with open(file) as f:
            reader = csv.reader(f)
            next(reader)
            user = User.objects.get(
                id=os.path.splitext(os.path.basename(file))[0]
            )
            Consumption.objects.bulk_create(
                [
                    Consumption(
                        user_id=user,
                        datetime=make_aware(
                            datetime.datetime.strptime(
                                row[0], '%Y-%m-%d %H:%M:%S'
                            )
                        ),
                        consumption=row[1],
                    ) for row in reader
                ]
            )

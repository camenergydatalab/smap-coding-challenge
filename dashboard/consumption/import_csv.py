from glob import glob
from dateutil.parser import parse

from consumption.models import User, Consumption

import csv
import os.path

def import_user(target_csv):
    with open(target_csv) as rf:
        reader = csv.DictReader(rf, delimiter=',')

        for row in reader:
            user, _created = User.objects.get_or_create(id=row['id'])
            user.area = row['area']
            user.tariff = row['tariff']
            user.save()


def import_consumption(target_dir):
    consumption_csv_files = glob("{}/*.csv".format(target_dir))

    for csv_file_path in consumption_csv_files:
        user_id = os.path.basename(csv_file_path).replace('.csv', '')
        if not User.objects.filter(id=user_id).exists():
            print('User {} is not registered yet.'.format(user_id))
            continue

        with open(csv_file_path) as rf:
            reader = csv.DictReader(rf, delimiter=',')

            for row in reader:
                consumption, _created = Consumption.objects.get_or_create(
                    user_id=user_id,
                    datetime=parse("{}+00:00".format(row['datetime'])),
                )
                consumption.consumption = row['consumption']
                consumption.save()

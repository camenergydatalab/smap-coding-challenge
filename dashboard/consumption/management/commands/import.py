import os
import pandas as pd
import pickle
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.db.models.functions import TruncDay
from sqlalchemy import create_engine

from consumption.constants import USER_DATA_PATH, USER_DATA_PICKLE_PATH, CONSUMPTION_DATA_PATH
from consumption.models import User, Consumption, CalculatedConsumption


class Command(BaseCommand):
    help = 'import data'

    def handle(self, *args, **options):
        start_time = time.perf_counter()

        database_name = settings.DATABASES['default']['NAME']
        database_url = f'sqlite:///{database_name}'
        engine = create_engine(database_url, echo=False)

        self._create_user(engine)
        self._create_consumption(engine)
        self._create_total_consumption()
        engine.dispose()

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f'処理にかかった時間: {elapsed_time}')
        print(f'userのレコード数: {User.objects.all().count()}')
        print(f'consumptionのレコード数: {Consumption.objects.all().count()}')
        print(f'total_consumptionのレコード数: {CalculatedConsumption.objects.all().count()}')

    def _create_user(self, engine):
        df_csv = pd.read_csv(USER_DATA_PATH, index_col='id', encoding='utf-8')

        if len(df_csv) == User.objects.all().count():
            return

        if os.path.isfile(USER_DATA_PICKLE_PATH):
            os.remove(USER_DATA_PICKLE_PATH)
        df_pickle = self._create_df_from_pickle_file(USER_DATA_PICKLE_PATH, df_csv)

        try:
            df_pickle.to_sql(name='consumption_user', con=engine, if_exists='append', index=True,
                             method='multi', chunksize=3000)
        except Exception as err:
            os.remove(USER_DATA_PICKLE_PATH)
            print(err)

    def _create_consumption(self, engine):
        users_id_list = User.objects.all().values_list('id', flat=True)
        for user_id in users_id_list:
            file_name = f"{CONSUMPTION_DATA_PATH}{user_id}.csv"
            df_csv = pd.read_csv(file_name, encoding='utf-8')
            df_not_duplicate = df_csv.drop_duplicates(subset='datetime')

            if len(df_not_duplicate) == Consumption.objects.filter(user_id=user_id).count():
                continue

            pickle_path = f'{CONSUMPTION_DATA_PATH}{user_id}.pickle'
            if os.path.isfile(pickle_path):
                os.remove(pickle_path)
            df_pickle = self._create_df_from_pickle_file(pickle_path, df_not_duplicate)
            df_pickle["user_id"] = user_id

            try:
                df_pickle.to_sql(name='consumption_consumption', con=engine, if_exists='append', index=False,
                                 method='multi', chunksize=3000)
            except Exception as err:
                os.remove(pickle_path)
                print(err)

    def _create_total_consumption(self):
        CalculatedConsumption.objects.all().delete()
        consumptions = Consumption.objects.annotate(date=TruncDay('datetime')).values('date').annotate(
            sum=Sum('consumption'))
        df = pd.DataFrame(list(consumptions))
        CalculatedConsumption.objects.bulk_create(CalculatedConsumption(**obj) for obj in df.to_dict('records'))

    def _create_df_from_pickle_file(self, pickle_path, df_csv):
        df_csv.to_pickle(pickle_path)
        with open(pickle_path, mode="rb") as pickle_data:
            return pickle.load(pickle_data)

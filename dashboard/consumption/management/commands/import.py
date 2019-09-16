import os
import pandas as pd
from tqdm import tqdm
import warnings
from django.core.management.base import BaseCommand

from consumption.models import UserReport, ConsumptionData

warnings.filterwarnings("ignore")


class Command(BaseCommand):
    help = "import data"

    def handle(self, *args, **options):
        data_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "..", "data"
        )
        fname = os.path.join(data_dir, "user_data.csv")
        user_data_df = pd.read_csv(fname)

        users_list = list(UserReport.objects.all().values_list("user_id", flat=True))
        total_consumption = ConsumptionData()
        for idx, user_data in tqdm(user_data_df.iterrows()):
            user_id = str(user_data["id"])
            if user_id in users_list:
                user_report = UserReport.objects.get(user_id=user_id)
            else:
                user_report = UserReport()
            user_report.user_id = user_id
            user_report.area = user_data["area"]
            user_report.tariff = user_data["tariff"]

            csv_name = os.path.join(data_dir, "consumption", f"{user_id}.csv")
            consumption_data = ConsumptionData()
            consumption_data.import_csv(csv_name)
            total_consumption.import_csv(csv_name)
            user_report.consumption_total = consumption_data.total
            user_report.consumption_avg = consumption_data.avg

            user_report.save()
        total_consumption.to_csv(os.path.join(data_dir, "consumption", "all.csv"))

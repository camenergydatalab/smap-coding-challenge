from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
import pandas as pd
from pathlib import Path
from consumption.models import User, Consumption, ConsumptionDetails
from datetime import timezone
from decimal import Decimal
from dataclasses import dataclass
from typing import List


@dataclass
class Command(BaseCommand):
    help: str = "import data"
    data_dir: Path = Path(__file__).parents[4] / "data"

    def _create_users(self, df: pd.DataFrame) -> None:
        """Userデータを作成する。

        Args:
            df (pd.DataFrame): user情報のDataFrame
        """
        users = []
        for _, row in df.iterrows():
            user = User()
            user.id = row["id"]
            user.area = row["area"]
            user.tariff = row["tariff"]
            users.append(user)
        User.objects.bulk_create(users, ignore_conflicts=True)

    def _create_consumptions(self, user_ids: List[int]) -> None:
        """日時ごとの消費量と日単位の消費量のデータを作成する

        Args:
            user_ids (List[int]): ユーザIDのリスト
        """
        consumptions = []
        consumption_details = []
        consumption_header = "consumption"
        datetime_header = "datetime"
        for id in user_ids:
            df = pd.read_csv(
                self.data_dir / consumption_header / f"{id}.csv",
                parse_dates=[datetime_header],
                index_col=datetime_header,
            )
            for date_time, row in df.iterrows():
                consumption = Consumption()
                consumption.user_id = id
                consumption.datetime = make_aware(date_time, timezone.utc)
                consumption.amount = Decimal(row[consumption_header])
                consumptions.append(consumption)
            for date, row in df.resample("D").sum().iterrows():
                consumption_detail = ConsumptionDetails()
                consumption_detail.user_id = id
                consumption_detail.date = date
                consumption_detail.total = row[consumption_header]
                consumption_details.append(consumption_detail)
        Consumption.objects.bulk_create(consumptions, ignore_conflicts=True)
        ConsumptionDetails.objects.bulk_create(
            consumption_details, ignore_conflicts=True
        )

    def handle(self, *args, **options):
        user_df = pd.read_csv(self.data_dir / "user_data.csv")
        self._create_users(user_df)
        users_ids = User.objects.all().values_list("id", flat=True)
        self._create_consumptions(users_ids)

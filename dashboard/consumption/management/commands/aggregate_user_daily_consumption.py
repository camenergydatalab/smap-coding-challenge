from django.core.management.base import BaseCommand
from consumption.models import Consumption, User, AggregateUserDailyConsumption
from django.db import transaction
from django.db.models import Avg, Sum
from datetime import datetime
import math

class Command(BaseCommand):
    help = 'Aggregate user consumption data by date'

    def handle(self, *args, **options):
        print("Aggregating User Daily Consumption")

        try:
            with transaction.atomic():
                # ユーザーごとに日付でグループ化し、合計と平均を計算
                user_daily_consumption_data = Consumption.objects.values('user', 'datetime__date').annotate(
                    total_consumption=Sum('consumption'),
                    average_consumption=Avg('consumption')
                )

                # AggregateUserDailyConsumption モデルに保存するデータをリストで作成
                data_to_insert = []
                for data in user_daily_consumption_data:
                    user_id = data['user']
                    date = data['datetime__date']
                    total_consumption = data['total_consumption']
                    average_consumption = math.floor(int(data['average_consumption']) * 10) / 10

                    data_to_insert.append(
                        AggregateUserDailyConsumption(
                            user_id=user_id,
                            date=date,
                            total_consumption=total_consumption,
                            average_consumption=average_consumption
                        )
                    )

                # バルクインサートを実行
                AggregateUserDailyConsumption.objects.bulk_create(data_to_insert)

            self.stdout.write(self.style.SUCCESS('User Daily Consumption data aggregated successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

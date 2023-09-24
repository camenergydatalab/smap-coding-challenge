from django.test import TestCase
from consumption.models import User, Consumption, AggregateUserDailyConsumption
from datetime import datetime

class UserModelTestCase(TestCase):
  def test_user_creation(self):
    user = User.objects.create(id=1, area="a1", tariff="t1")
    self.assertEqual(user.id, 1)
    self.assertEqual(user.area, "a1")
    self.assertEqual(user.tariff, "t1")


class ConsumptionModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(id=1, area="a1", tariff="t1")

    def test_consumption_creation(self):
        datetime_str = "2023-09-12 00:00:00"
        consumption = Consumption.objects.create(
            datetime=datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S'),
            consumption=50.0,
            user=self.user
        )
        self.assertEqual(consumption.datetime.strftime('%Y-%m-%d %H:%M:%S'), datetime_str)
        self.assertEqual(consumption.consumption, 50.0)
        self.assertEqual(consumption.user, self.user)

class AggregateUserDailyConsumptionModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(id=1, area="a1", tariff="t1")

    def test_aggregate_user_daily_consumption_creation(self):
        date_str = "2023-09-12"
        aggregate = AggregateUserDailyConsumption.objects.create(
            user=self.user,
            date=datetime.strptime(date_str, '%Y-%m-%d'),
            total_consumption=100.0,
            average_consumption=25.0
        )
        self.assertEqual(aggregate.user, self.user)
        self.assertEqual(aggregate.date.strftime('%Y-%m-%d'), date_str)
        self.assertEqual(aggregate.total_consumption, 100.0)
        self.assertEqual(aggregate.average_consumption, 25.0)

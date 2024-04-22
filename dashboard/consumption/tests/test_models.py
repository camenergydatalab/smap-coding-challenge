from django.test import TestCase
from ..models import User, Consumption
from datetime import datetime, timezone


class UserModelTests(TestCase):
    def test_is_empty(self):
        # 初期状態チェック
        saved_users = User.objects.all()
        self.assertEqual(saved_users.count(), 0)

    def test_create_action(self):
        # 生成動作チェック
        user = User(user_id=1, user_area='test_area', user_tariff='test_tariff')
        user.save()
        saved_users = User.objects.all()
        self.assertEqual(saved_users.count(), 1)

    def test_saved_user_data(self):
        # 保存データチェック
        user = User()
        user_id = 1
        user_area = 'test_area'
        user_tariff = 'test_tariff'
        user.user_id = user_id
        user.user_area = user_area
        user.user_tariff = user_tariff
        user.save()

        saved_users = User.objects.all()
        actual_user = saved_users[0]

        self.assertEqual(actual_user.user_id, user_id)
        self.assertEqual(actual_user.user_area, user_area)
        self.assertEqual(actual_user.user_tariff, user_tariff)


class ConsumptionModelTests(TestCase):
    def test_is_empty(self):
        # 初期状態チェック
        saved_consumptions = Consumption.objects.all()
        self.assertEqual(saved_consumptions.count(), 0)

    def test_create_action(self):
        # 生成動作チェック
        user = User(user_id=1, user_area='test_area', user_tariff='test_tariff')
        user.save()
        consumption = Consumption(user_id=user, cousumption_datetime=datetime.now(), cousumption_value=123)
        consumption.save()
        saved_consumptions = Consumption.objects.all()
        self.assertEqual(saved_consumptions.count(), 1)

    def test_saved_cunsumption_data(self):
        # 保存データチェック
        consumption = Consumption()
        user = User(user_id=1, user_area='test_area', user_tariff='test_tariff')
        user.save()
        datetime_now = datetime.now(timezone.utc)
        cousumption_datetime = datetime_now
        cousumption_value = 123
        consumption.user_id = user
        consumption.cousumption_datetime = cousumption_datetime
        consumption.cousumption_value = cousumption_value
        consumption.save()

        saved_cousumptions = Consumption.objects.all()
        actual_cousumption = saved_cousumptions[0]

        self.assertEqual(actual_cousumption.user_id, user)
        self.assertEqual(actual_cousumption.cousumption_datetime, cousumption_datetime)
        self.assertEqual(actual_cousumption.cousumption_value, cousumption_value)

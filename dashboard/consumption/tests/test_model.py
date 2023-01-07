import datetime
from operator import attrgetter

from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase
from django.utils.timezone import make_aware

from consumption.models import UserData, ConsumptionData

# 日時データ
dt = datetime.datetime.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
dt = make_aware(dt)


class UserDataTest(TestCase):
    def test_empty(self):
        """ ユーザデータが登録されていないこと """

        users = UserData.objects.all()
        self.assertQuerysetEqual(users, [])

    def test_one_user(self):
        """ ユーザデータが作成できること """

        UserData.objects.create(id="1000", area="a1", tariff="t1")
        users = UserData.objects.all().order_by("pk")
        self.assertQuerysetEqual(
            users,
            [(1000, "a1", "t1")],
            transform=attrgetter("id", "area", "tariff"),
            ordered=False
        )


class UserDataTransactionTests(TransactionTestCase):
    def test_error_same_id_create(self):
        """ 同じIDでユーザデータが作成時にエラーが出ること """

        user_data = dict(id="1000", area="a1", tariff="t1")
        UserData.objects.create(**user_data)

        with self.assertRaisesMessage(
                IntegrityError,
                "UNIQUE constraint failed: consumption_userdata.id"
        ):
            UserData.objects.create(**user_data)


class ConsumptionDataTests(TestCase):
    def test_empty(self):
        consumption_data = ConsumptionData.objects.all()
        self.assertQuerysetEqual(consumption_data, [])

    def test_error_create_data_no_userdata(self):
        """ ユーザデータなしでデータが登録できないこと """

        consumption_data = ConsumptionData(datetime=dt, consumption=100.0)

        with self.assertRaisesMessage(
                IntegrityError,
                "NOT NULL constraint failed: consumption_consumptiondata.user_id"
        ):
            consumption_data.save()

    def test_error_create_data_no_timedate(self):
        """ 日時データなしでデータが登録できないこと """
        user_data = UserData.objects.create(id="1000", area="a1", tariff="t1")
        consumption_data = ConsumptionData(user=user_data, datetime=None, consumption=100.0)

        with self.assertRaisesMessage(
                IntegrityError,
                "NOT NULL constraint failed: consumption_consumptiondata.datetime"
        ):
            consumption_data.save()

    def test_error_create_data_invalid_consumption(self):
        """ 消費量データなしでデータが登録できないこと """
        user_data = UserData.objects.create(id="1000", area="a1", tariff="t1")
        consumption_data = ConsumptionData(user=user_data, datetime=dt, consumption=None)

        with self.assertRaisesMessage(
                IntegrityError,
                "NOT NULL constraint failed: consumption_consumptiondata.consumption"
        ):
            consumption_data.save()

    def test_one_data(self):
        """ データが作成できること """
        user_data = UserData.objects.create(id="1000", area="a1", tariff="t1")

        ConsumptionData.objects.create(user=user_data, datetime=dt, consumption=100.0)

        consumption_data = ConsumptionData.objects.all()
        self.assertQuerysetEqual(
            consumption_data,
            [(1000, 100.0)],
            transform=attrgetter("user_id", "consumption")
        )

    def test_same_date_create_data(self):
        """ 同じユーザ、同じ日時でデータが作成
            TODO: 同じ日時でデータは作成できない方が良いか
        """

        user_data = UserData.objects.create(id="1000", area="a1", tariff="t1")

        ConsumptionData.objects.bulk_create([
            # 同じ日時
            ConsumptionData(user=user_data, datetime=dt, consumption=100.0),
            ConsumptionData(user=user_data, datetime=dt, consumption=110.0)
        ])

        consumption_data = ConsumptionData.objects.all()
        self.assertQuerysetEqual(
            consumption_data,
            [(1000, dt, 100.0), (1000, dt, 110.0)],
            transform=attrgetter("user_id", "datetime", "consumption"),
            ordered=False
        )

    def test_get_data_from_user(self):
        """ ユーザデータから消費量データを取得できること """
        user_data_1 = UserData.objects.create(id="1000", area="a1", tariff="t1")
        user_data_2 = UserData.objects.create(id="2000", area="a1", tariff="t1")
        user_data_3 = UserData.objects.create(id="3000", area="a1", tariff="t1")

        ConsumptionData.objects.create(user=user_data_1, datetime=dt, consumption=101.0)
        ConsumptionData.objects.create(user=user_data_1, datetime=dt.replace(day=2), consumption=102.0)
        ConsumptionData.objects.create(user=user_data_1, datetime=dt.replace(day=3), consumption=103.0)

        ConsumptionData.objects.create(user=user_data_2, datetime=dt, consumption=201.0)

        with self.subTest("作成したデータが取得できていること"):
            self.assertQuerysetEqual(
                user_data_1.consumptiondata_set.all().order_by("pk"),
                [(1000, 101.0), (1000, 102.0), (1000, 103.0)],
                transform=attrgetter("user_id", "consumption")
            )

        with self.subTest("作成していない場合は空データが返ってくること"):
            self.assertQuerysetEqual(
                user_data_3.consumptiondata_set.all().order_by("pk"),
                [],
                transform=attrgetter("user_id", "consumption")
            )

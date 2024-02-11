# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from ..models import Area, Consumption, Tariff, User
from ..repository.consumption_repository import ConsumptionRepository
from ..repository.user_repository import UserRepository


class UserRepositoryTest(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name="a1")
        self.tariff = Tariff.objects.create(plan="t1")

    def test_bulk_insert(self):
        user_models = [
            User(id=5000, area=self.area, tariff=self.tariff),
            User(id=5001, area=self.area, tariff=self.tariff),
            User(id=5002, area=self.area, tariff=self.tariff),
        ]

        UserRepository.bulk_insert(user_models)

        self.assertEqual(User.objects.all().count(), 3)

    def test_get_all(self):
        User.objects.all().delete()

        user_models = [
            User(id=5000, area=self.area, tariff=self.tariff),
            User(id=5001, area=self.area, tariff=self.tariff),
            User(id=5002, area=self.area, tariff=self.tariff),
        ]

        UserRepository.bulk_insert(user_models)

        users = UserRepository.get_all()

        self.assertEqual(users.count(), 3)


class ConsumptionRepositoryTest(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name="a1")
        self.tariff = Tariff.objects.create(plan="t1")
        self.user = User.objects.create(id=3000, area=self.area, tariff=self.tariff)

    def set_test_data(self):
        Consumption.objects.all().delete()

        test_datetimes = [
            timezone.make_aware(datetime(2016, 7, 1, 0, 0, 0)),
            timezone.make_aware(datetime(2016, 7, 1, 1, 0, 0)),
            timezone.make_aware(datetime(2016, 7, 2, 0, 0, 0)),
            timezone.make_aware(datetime(2016, 8, 1, 0, 0, 0)),
            timezone.make_aware(datetime(2016, 8, 2, 0, 0, 0)),
            timezone.make_aware(datetime(2016, 9, 1, 0, 0, 0)),
            timezone.make_aware(datetime(2016, 9, 2, 0, 0, 0)),
            timezone.make_aware(datetime(2016, 10, 1, 0, 0, 0)),
            timezone.make_aware(datetime(2016, 10, 2, 0, 0, 0)),
            timezone.make_aware(datetime(2016, 11, 1, 0, 0, 0)),
            timezone.make_aware(datetime(2016, 11, 2, 0, 0, 0)),
            timezone.make_aware(datetime(2016, 12, 1, 0, 0, 0)),
            timezone.make_aware(datetime(2016, 12, 2, 0, 0, 0)),
        ]

        for d in test_datetimes:
            Consumption.objects.create(
                user=self.user,
                datetime=d,
                value=300.0,
            )

    def test_bulk_insert(self):
        consumption_models = [
            Consumption(
                user=self.user,
                datetime=timezone.make_aware(datetime(2016, 7, 15, 0, 0, 0)),
                value=100.0,
            ),
            Consumption(
                user=self.user,
                datetime=timezone.make_aware(datetime(2016, 7, 15, 0, 30, 0)),
                value=200.0,
            ),
            Consumption(
                user=self.user,
                datetime=timezone.make_aware(datetime(2016, 7, 15, 1, 0, 0)),
                value=300.0,
            ),
        ]

        ConsumptionRepository.bulk_insert(consumption_models)

        self.assertEqual(Consumption.objects.all().count(), 3)

    def test_get_period_start_end_day(self):
        """集計期間の開始日と終了日を取得できるか"""
        self.set_test_data()

        self.assertEqual(
            ConsumptionRepository.get_period_start_end_day(),
            {
                "start": "2016-07-01",
                "end": "2016-12-02",
            },
        )

    def test_get_total_period_months(self):
        """全集計期間月をリストで取得できるか"""

        self.set_test_data()

        self.assertEqual(
            ConsumptionRepository.get_total_period_months(),
            [
                "2016-07",
                "2016-08",
                "2016-09",
                "2016-10",
                "2016-11",
                "2016-12",
            ],
        )

    def test_get_total_value_per_month(self):
        """月別消費量を取得できるか"""

        self.set_test_data()

        self.assertEqual(
            ConsumptionRepository.get_total_value_per_month(),
            {
                "2016-07": 900,
                "2016-08": 600,
                "2016-09": 600,
                "2016-10": 600,
                "2016-11": 600,
                "2016-12": 600,
            },
        )

    def test_get_daily_average_value_per_month(self):
        """月別に1日あたりの平均消費量を取得できるか"""
        self.set_test_data()

        self.assertEqual(
            ConsumptionRepository.get_daily_average_value_per_month(),
            {
                "2016-07": 300,
                "2016-08": 300,
                "2016-09": 300,
                "2016-10": 300,
                "2016-11": 300,
                "2016-12": 300,
            },
        )

    def test_get_total_value_per_month_by_user_id(self):
        """ユーザIDを引数に月別消費量を取得できるか"""

        self.set_test_data()

        self.assertEqual(
            ConsumptionRepository.get_total_value_per_month_by_user_id(self.user),
            {
                "2016-07": 900,
                "2016-08": 600,
                "2016-09": 600,
                "2016-10": 600,
                "2016-11": 600,
                "2016-12": 600,
            },
        )

    def test_get_total_value_by_user_id(self):
        """ユーザIDを引数に合計消費量を取得できるか"""

        self.set_test_data()

        self.assertEqual(
            ConsumptionRepository.get_total_value_by_user_id(self.user), 3900
        )

    def test_get_daily_average_value_per_month_by_user_id(self):
        """ユーザIDを引数に月別に1日あたりの平均消費量を取得できるか"""
        self.set_test_data()

        self.assertEqual(
            ConsumptionRepository.get_daily_average_value_per_month_by_user_id(
                self.user
            ),
            {
                "2016-07": 300,
                "2016-08": 300,
                "2016-09": 300,
                "2016-10": 300,
                "2016-11": 300,
                "2016-12": 300,
            },
        )

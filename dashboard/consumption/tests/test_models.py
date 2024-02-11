# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from ..init_datas import AREAS, TARIFFS
from ..models import Area, Consumption, Tariff, User


# Create your tests here.
class AreaTests(TestCase):
    def setUp(self):
        for _area in AREAS:
            Area.objects.create(name=_area[1])

    def test_model_str(self):
        model = Area.objects.get(name="a1")
        self.assertEqual(str(model), "a1")


class TariffTests(TestCase):
    def setUp(self):
        for _tariff in TARIFFS:
            Tariff.objects.create(plan=_tariff[1])

    def test_model_str(self):
        model = Tariff.objects.get(plan="t1")
        self.assertEqual(str(model), "t1")


class UserTests(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name="a1")
        self.tariff = Tariff.objects.create(plan="t1")
        User.objects.create(id=3000, area=self.area, tariff=self.tariff)

    def test_model_str(self):
        model = User.objects.get(id=3000)
        self.assertEqual(str(model), "3000")

    def test_unique_id(self):
        """IDが重複しているに発生するユニーク制約の例外確認"""
        with self.assertRaises(IntegrityError):
            User.objects.create(id=3000, area=self.area, tariff=self.tariff)

    def test_bulk_insert(self):
        """バルクインサート"""
        users = [
            User(id=5000, area=self.area, tariff=self.tariff),
            User(id=5001, area=self.area, tariff=self.tariff),
            User(id=5002, area=self.area, tariff=self.tariff),
        ]

        User.objects.bulk_create(users)
        self.assertEqual(User.objects.all().count(), 4)


class ConsumptionTests(TestCase):
    def setUp(self):
        self.aware_datetime = timezone.make_aware(datetime(2016, 7, 15, 0, 0, 0))

        self.area = Area.objects.create(name="a1")
        self.tariff = Tariff.objects.create(plan="t1")
        self.user = User.objects.create(id=3000, area=self.area, tariff=self.tariff)
        Consumption.objects.create(
            user=self.user, datetime=self.aware_datetime, value=39.0
        )

    def test_user_datetime_unique(self):
        """ユーザと日時が重複しているに発生するユニーク制約の例外確認"""
        with self.assertRaises(IntegrityError):
            Consumption.objects.create(
                user=self.user, datetime=self.aware_datetime, value=39.0
            )

    def test_bulk_insert(self):
        """バルクインサート"""
        consumptions = [
            Consumption(
                user=self.user,
                datetime=timezone.make_aware(datetime(2016, 7, 15, 1, 0, 0)),
                value=39.0,
            ),
            Consumption(
                user=self.user,
                datetime=timezone.make_aware(datetime(2016, 7, 15, 2, 0, 0)),
                value=39.0,
            ),
            Consumption(
                user=self.user,
                datetime=timezone.make_aware(datetime(2016, 7, 15, 3, 0, 0)),
                value=39.0,
            ),
        ]

        Consumption.objects.bulk_create(consumptions)
        self.assertEqual(Consumption.objects.all().count(), 4)

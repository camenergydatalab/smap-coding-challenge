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

    def test_bulk_insert(self):
        consumptions = [
            {
                "user": self.user,
                "datetime": timezone.make_aware(datetime(2016, 7, 15, 0, 0, 0)),
                "value": 100.0,
            },
            {
                "user": self.user,
                "datetime": timezone.make_aware(datetime(2016, 7, 15, 0, 30, 0)),
                "value": 200.0,
            },
            {
                "user": self.user,
                "datetime": timezone.make_aware(datetime(2016, 7, 15, 1, 0, 0)),
                "value": 300.0,
            },
        ]

        ConsumptionRepository.bulk_insert(consumptions)

        self.assertEqual(Consumption.objects.all().count(), 3)

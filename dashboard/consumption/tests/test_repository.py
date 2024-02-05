# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from ..models import Area, Tariff, User
from ..repository.user_repository import UserRepository


class UserRepositoryTest(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name="a1")
        self.tariff = Tariff.objects.create(plan="t1")

    def test_bulk_insert(self):
        users = [
            {"id": 5000, "area": self.area, "tariff": self.tariff},
            {"id": 5001, "area": self.area, "tariff": self.tariff},
            {"id": 5002, "area": self.area, "tariff": self.tariff},
        ]

        UserRepository.bulk_insert(users)

        self.assertEqual(User.objects.all().count(), 3)

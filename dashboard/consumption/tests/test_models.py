# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.utils import IntegrityError
from django.test import TestCase

from ..init_datas import AREAS, TARIFFS
from ..models import Area, Tariff, User


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
        User.objects.create(
            id=3000,
            area=self.area,
            tariff=self.tariff
        )

    def test_model_str(self):
        model = User.objects.get(id=3000)
        self.assertEqual(str(model), "3000")

    def test_unique_id(self):
        """IDが重複しているに発生するユニーク制約の例外確認"""
        with self.assertRaises(IntegrityError):
            User.objects.create(
                id=3000,
                area=self.area,
                tariff=self.tariff
            )

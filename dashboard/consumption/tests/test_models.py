# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from ..init_datas import AREAS, TARIFFS
from ..models import Area, Tariff


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

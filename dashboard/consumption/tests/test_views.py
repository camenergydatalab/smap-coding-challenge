# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import Client, TestCase

from ..models import Area, Consumption, Tariff, User


# Create your tests here.
class SummaryViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_top_path(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_summary_path(self):
        response = self.client.get("/summary/")
        self.assertEqual(response.status_code, 200)


class DetailViewTests(TestCase):
    def setUp(self):
        area = Area.objects.create(name="a1")
        tariff = Tariff.objects.create(plan="t1")
        self.user = User.objects.create(id=3000, area=area, tariff=tariff)

        self.client = Client()

    def test_detail_path(self):
        response = self.client.get("/detail/" + str(self.user.id) + "/")
        self.assertEqual(response.status_code, 200)

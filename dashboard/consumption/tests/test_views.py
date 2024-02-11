# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import Client, TestCase


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
        self.client = Client()

    def test_detail_path(self):
        response = self.client.get("/detail/")
        self.assertEqual(response.status_code, 200)

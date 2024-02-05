# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from decimal import Decimal
from django.core.cache import cache
from django.test import TestCase
from django.utils.timezone import get_default_timezone
from typing import Any

from .models import Consumer, Consumption


class QueryAPITestCase(TestCase):
    def setUp(self):
        cache.clear()
        consumer = Consumer.objects.create(id=10000, area="a1", tariff="t1")
        self.c1100 = Consumption.objects.create(consumer=consumer, datetime=datetime(1999, 1, 1, 0, 0, tzinfo=get_default_timezone()), amount=Decimal("1.0"))
        self.c1103 = Consumption.objects.create(consumer=consumer, datetime=datetime(1999, 1, 1, 0, 30, tzinfo=get_default_timezone()), amount=Decimal("2.0"))
        self.c1110 = Consumption.objects.create(consumer=consumer, datetime=datetime(1999, 1, 1, 1, 0, tzinfo=get_default_timezone()), amount=Decimal("4.0"))
        self.c1200 = Consumption.objects.create(consumer=consumer, datetime=datetime(1999, 1, 2, 0, 0, tzinfo=get_default_timezone()), amount=Decimal("8.0"))
        self.c2100 = Consumption.objects.create(consumer=consumer, datetime=datetime(1999, 2, 1, 0, 0, tzinfo=get_default_timezone()), amount=Decimal("16.0"))
        consumer2 = Consumer.objects.create(id=10001, area="a1", tariff="t1")
        self.cc2 = Consumption.objects.create(consumer=consumer2, datetime=datetime(1999, 1, 1, 0, 0, tzinfo=get_default_timezone()), amount=Decimal("32.0"))

    def test_query(self):
        self.assertJsonResponseData(
            "/query",
            [
                ["1999-01-01", 39, 2],
                ["1999-01-02", 8, 1],
                ["1999-02-01", 16, 1]
            ],
        )
        self.assertJsonResponseData(
            "/query?grouper=no",
            [
                ["1999-01-01 00:00:00", 33, 2],
                ["1999-01-01 00:30:00", 2, 1],
                ["1999-01-01 01:00:00", 4, 1],
                ["1999-01-02 00:00:00", 8, 1],
                ["1999-02-01 00:00:00", 16, 1],
            ],
        )
        self.assertJsonResponseData(
            "/query?grouper=monthly-by-year",
            [
                ["01", 47, 2],
                ["02", 16, 1],
            ],
        )
        self.assertJsonResponseData(
            "/query?grouper=hourly-by-day",
            [
                ["00", 59, 2],
                ["01", 4, 1],
            ],
        )

    def test_error(self):
        res = self.client.get("/query?consumer_id=xxxxx")
        self.assertEqual(res.status_code, 400, "request did not failed")
        self.assertEqual(res["Content-Type"], "application/json",
                         "wrong content type")
        j = res.json()
        self.assertNotEqual(j["errno"], 0, "errno is 0")
        self.assertIsInstance(j["message"], str, "message is not a string")
        self.assertEqual(j["data"], None, "data is not null")

    def assertJsonResponseData(self, url: str, expected: Any, msg: str = None):
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200, "request failed")
        self.assertEqual(res["Content-Type"], "application/json", "wrong content type")
        j = res.json()
        self.assertEqual(j["errno"], 0, "errno is not 0")
        self.assertIsInstance(j["message"], str, "message is not a string")
        self.assertSequenceEqual(j["data"], expected, f"wrong return value when testing {url}")

    def test_cache(self):
        self.assertJsonResponseData(
            "/query",
            [
                ["1999-01-01", 39, 2],
                ["1999-01-02", 8, 1],
                ["1999-02-01", 16, 1]
            ],
        )
        self.c1100.amount = Decimal("64.0")
        self.c1100.save()
        self.assertJsonResponseData(
            "/query",
            [
                ["1999-01-01", 39, 2],
                ["1999-01-02", 8, 1],
                ["1999-02-01", 16, 1]
            ],
        )
        self.assertJsonResponseData(
            "/query?force_refresh=1",
            [
                ["1999-01-01", 102, 2],
                ["1999-01-02", 8, 1],
                ["1999-02-01", 16, 1]
            ],
        )


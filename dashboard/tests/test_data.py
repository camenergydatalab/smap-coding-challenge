# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
import pytz

from django.test import TransactionTestCase
from consumption.models import Consumption, User


# Definition of Mock User info
USER_1 = 1234
USER_2 = 1111
USER_3 = 3333

USER_DATA_1 = {
    "id": USER_1,
    "area": 'a1',
    "tariff": 't1',
}

USER_DATA_2 = {
    "id": USER_2,
    "area": 'a2',
    "tariff": 't2',
}

USER_DATA_3 = {
    "id": USER_3,
    "area": 'a3',
    "tariff": 't3',
}

# Definition of Mock Cousumption info
TEST_DATETIME_1 = pytz.utc.localize(datetime(2021, 1, 1, 00, 30, 00))
TEST_DATETIME_2 = pytz.utc.localize(datetime(2021, 1, 1, 1, 00, 00))
TEST_DATETIME_3 = pytz.utc.localize(datetime(2021, 1, 1, 1, 30, 00))

CONSUM_DATA_USER_1_1 = {
    "id": 11111,
    "user_id": USER_1,
    "datetime": TEST_DATETIME_1,
    'consumption': 100
}

CONSUM_DATA_USER_1_2 = {
    "id": 11112,
    "user_id": USER_1,
    "datetime": TEST_DATETIME_2,
    'consumption': 200
}

CONSUM_DATA_USER_1_3 = {
    "id": 11113,
    "user_id": USER_1,
    "datetime": TEST_DATETIME_3,
    'consumption': 300
}

CONSUM_DATA_USER_2_1 = {
    "id": 22221,
    "user_id": USER_2,
    "datetime": TEST_DATETIME_1,
    'consumption': 400
}

CONSUM_DATA_USER_2_2 = {
    "id": 22222,
    "user_id": USER_2,
    "datetime": TEST_DATETIME_2,
    'consumption': 500
}

CONSUM_DATA_USER_2_3 = {
    "id": 22223,
    "user_id": USER_2,
    "datetime": TEST_DATETIME_3,
    'consumption': 600
}

CONSUM_DATA_USER_3_1 = {
    "id": 33331,
    "user_id": USER_3,
    "datetime": TEST_DATETIME_1,
    'consumption': 700
}

CONSUM_DATA_USER_3_2 = {
    "id": 33332,
    "user_id": USER_3,
    "datetime": TEST_DATETIME_2,
    'consumption': 800
}

CONSUM_DATA_USER_3_3 = {
    "id": 33333,
    "user_id": USER_3,
    "datetime": TEST_DATETIME_3,
    'consumption': 900
}


class UserTestData(TransactionTestCase):
    """
    set up User data
    """
    databases = '__all__'

    @classmethod
    def setUp(cls, data):
        User.objects.create(
            id=data["id"],
            area=data["area"],
            tariff=data["tariff"]
        )


class ConsumptionTestData(TransactionTestCase):
    """
    set up Consumption data
    """
    databases = '__all__'

    @classmethod
    def setUp(cls, data):
        Consumption.objects.create(
            id=data["id"],
            user_id=User.objects.get(id=data["user_id"]),
            datetime=data["datetime"],
            consumption=data["consumption"]
        )

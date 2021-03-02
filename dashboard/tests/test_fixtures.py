# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import platform

from datetime import datetime
import pytz

from django.test import TransactionTestCase
from django.conf import settings
from consumption.models import Consumption, User


BASE_DIR = getattr(settings, "BASE_DIR", None)
TEST_DIR = os.path.join(BASE_DIR, 'tests')
UNIT_TEST_DIR = os.path.join(TEST_DIR, 'unittest')
INTEG_TEST_DIR = os.path.join(TEST_DIR, 'integtest')


def get_driver_path():
    driver = platform.system()
    if driver == 'Darwin':  # Mac OS
        return os.path.join(INTEG_TEST_DIR, 'driver/mac/chromedriver')
    # TODO: if need another OS, new definition need here


# DRIVER_PATH = get_driver_path()

SELENIUM_SETTING = {
    'chromedriver_path': get_driver_path(),
    # 'binary_location': '/usr/bin/chromium-browser', # use if need
    'headless': '--headless',
    'disable-gpu': '--disable-gpu',
    'no-sandbox': '--no-sandbox',
    'window-size': '--window-size=1024x1024'
}


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
TEST_DATETIME_1 = pytz.utc.localize(datetime(2021, 1, 1, 00, 00, 00))
TEST_DATETIME_2 = pytz.utc.localize(datetime(2021, 1, 1, 00, 30, 00))
TEST_DATETIME_3 = pytz.utc.localize(datetime(2021, 1, 1, 1, 00, 00))
TEST_DATETIME_4 = pytz.utc.localize(datetime(2021, 1, 2, 00, 00, 00))
TEST_DATETIME_5 = pytz.utc.localize(datetime(2021, 1, 3, 00, 00, 00))

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

CONSUM_DATA_USER_1_4 = {
    "id": 11114,
    "user_id": USER_1,
    "datetime": TEST_DATETIME_4,
    'consumption': 400
}

CONSUM_DATA_USER_1_5 = {
    "id": 11115,
    "user_id": USER_1,
    "datetime": TEST_DATETIME_5,
    'consumption': 500
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

CONSUM_DATA_USER_2_4 = {
    "id": 22224,
    "user_id": USER_2,
    "datetime": TEST_DATETIME_4,
    'consumption': 400
}

CONSUM_DATA_USER_2_5 = {
    "id": 22225,
    "user_id": USER_2,
    "datetime": TEST_DATETIME_5,
    'consumption': 500
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

CONSUM_DATA_USER_3_4 = {
    "id": 33334,
    "user_id": USER_3,
    "datetime": TEST_DATETIME_4,
    'consumption': 400
}

CONSUM_DATA_USER_3_5 = {
    "id": 33335,
    "user_id": USER_3,
    "datetime": TEST_DATETIME_5,
    'consumption': 500
}


class UserTestData(TransactionTestCase):
    """
    set up User data
    """
    @classmethod
    def setUp(cls, data):
        """set up user data

        Create given user's data

        Args:
            data (dict):
                {
                    "id": Number,
                    "area": String,
                    "tariff": String,
                }
        """
        User.objects.create(
            id=data["id"],
            area=data["area"],
            tariff=data["tariff"]
        )


class ConsumptionTestData(TransactionTestCase):
    """
    set up Consumption data
    """

    @classmethod
    def setUp(cls, data):
        """set up user data

        Create given user's data

        Args:
            data (dict):
                {
                    "id": Integer,
                    "user_id": String,
                    "datetime": DateTime Object,
                    "consumption": Float or Decimal
                }
        """
        Consumption.objects.create(
            id=data["id"],
            user_id=User.objects.get(id=data["user_id"]),
            datetime=data["datetime"],
            consumption=data["consumption"]
        )

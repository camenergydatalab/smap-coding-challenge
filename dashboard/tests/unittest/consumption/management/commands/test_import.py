# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import importlib
import io
import os
from unittest.mock import MagicMock, call, patch

from django.test import TransactionTestCase
from django.utils.timezone import make_aware

from consumption.models import Consumption, User

import_mod_path = 'consumption.management.commands.import'
import_mod = importlib.import_module(import_mod_path)

dummy_user_data = """id,area,tariff
1111,a1,t1
2222,a2,t2
3333,a3,t3
"""

dummy_cusum_data = """datetime,consumption
2016-07-15 00:00:00,39.0
2016-07-15 00:30:00,147.0
2016-07-15 01:00:00,134.0
"""


class CommandTestcase(TransactionTestCase):
    databases = '__all__'
    dummy_user_id = 1111

    @patch.object(import_mod.Command, 'get_user_data', MagicMock(
        return_value='get_user_data called'))
    @patch.object(import_mod.Command, 'read_user', MagicMock())
    @patch.object(import_mod.Command, 'get_consumption_data_list', MagicMock(
        return_value=['data_1.csv', 'data_2.csv']))
    @patch.object(import_mod.Command, 'read_consumption', MagicMock())
    def test_handle(self):
        command = import_mod.Command()
        # execute
        command.handle()
        command.get_user_data.assert_called()
        command.read_user.assert_called_with('get_user_data called')
        command.get_consumption_data_list.assert_called()
        command.read_consumption.assert_has_calls(
            [
                call('data_1.csv'),
                call('data_2.csv')
            ]
        )

    @patch.object(import_mod, 'DATA_DIR', 'data dir')
    @patch.object(import_mod, 'USER_DATA_FILE', 'user data')
    def test_get_user_data(self):
        command = import_mod.Command()
        # execute
        expected = os.path.join('data dir', 'user data')
        result = command.get_user_data()
        self.assertEqual(result, expected)

    @patch.object(import_mod, 'DATA_DIR', 'data dir')
    @patch.object(import_mod, 'CONSUM_DATA_DIR_NAME', 'consum data dir')
    @patch.object(import_mod, 'listdir', MagicMock(
        return_value=['data_1.csv', 'data_2.csv']))
    @patch.object(import_mod, 'isfile', MagicMock(return_value=True))
    def test_get_consumption_data_list(self):
        command = import_mod.Command()
        # execute
        expected = [
            os.path.abspath(
                os.path.join('data dir/consum data dir', f)
            ) for f in ['data_1.csv', 'data_2.csv']
        ]
        result = command.get_consumption_data_list()
        self.assertEqual(result, expected)

    # mock open and return dummy data
    @patch.object(import_mod, 'open', MagicMock(
        return_value=io.StringIO(dummy_user_data)))
    def test_read_user(self):
        command = import_mod.Command()
        # execute
        command.read_user('dummy')

        # user 1
        user_1 = User.objects.get(id=1111)
        self.assertEqual(user_1.area, 'a1')
        self.assertEqual(user_1.tariff, 't1')
        # user 2
        user_1 = User.objects.get(id=2222)
        self.assertEqual(user_1.area, 'a2')
        self.assertEqual(user_1.tariff, 't2')
        # user 3
        user_1 = User.objects.get(id=3333)
        self.assertEqual(user_1.area, 'a3')
        self.assertEqual(user_1.tariff, 't3')

    # mock open and return dummy data
    @patch.object(import_mod, 'open', MagicMock(
        return_value=io.StringIO(dummy_cusum_data)))
    def test_read_consumption(self):
        # prepare dummy user
        User.objects.create(id=self.dummy_user_id, area='a1', tariff='t1')

        command = import_mod.Command()
        # execute with dummy user id
        command.read_consumption(str(self.dummy_user_id))

        # cumsumption data
        user = User.objects.get(id=self.dummy_user_id)
        cumsum_data = Consumption.objects.filter(user_id=user)

        # 1st data
        self.assertEqual(
            cumsum_data[0].datetime,
            make_aware(datetime.datetime.strptime(
                '2016-07-15 00:00:00', '%Y-%m-%d %H:%M:%S'
            ))
        )
        self.assertEqual(cumsum_data[0].consumption, 39.0)

        # 2nd data
        self.assertEqual(
            cumsum_data[1].datetime,
            make_aware(datetime.datetime.strptime(
                '2016-07-15 00:30:00', '%Y-%m-%d %H:%M:%S'
            ))
        )
        self.assertEqual(cumsum_data[1].consumption, 147.0)

        # 3rd data
        self.assertEqual(
            cumsum_data[2].datetime,
            make_aware(datetime.datetime.strptime(
                '2016-07-15 01:00:00', '%Y-%m-%d %H:%M:%S'
            ))
        )
        self.assertEqual(cumsum_data[2].consumption, 134.0)

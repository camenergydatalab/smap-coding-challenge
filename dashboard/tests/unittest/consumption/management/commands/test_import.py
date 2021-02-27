# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import datetime
import importlib
import os
import shutil
import sys
from os import listdir
from os.path import isfile, join
from unittest.mock import MagicMock

from consumption.models import Consumption, User
from django.conf import settings
from django.test import TransactionTestCase
from django.utils.timezone import make_aware


# module for test
import_mod_path = 'consumption.management.commands.import'

# definition for mock
BASE_DIR = getattr(settings, "BASE_DIR", None)
MOCK_DATA_DIR = os.path.join(BASE_DIR, 'tests/unittest/test_data')
MOCK_DUP_DATA_DIR = os.path.join(MOCK_DATA_DIR, 'duplicated')
MOCK_NON_DUP_DATA_DIR = os.path.join(MOCK_DATA_DIR, 'non_duplicated')
MOCK_USER_DATA_FILE = 'user_data.csv'
MOCK_CONSUM_DATA_DIR = 'consumption'
MOCK_VALIDATION_DIR = os.path.join(MOCK_DATA_DIR, 'validation_results')
MOCK_DUP_RESULT_DIR_NAME = 'duplicated'

MOCK_USER_ID_1 = 1111
MOCK_USER_ID_2 = 2222
MOCK_USER_ID_3 = 3333

# Definition of Mock Cousumption info
MOCK_CSV_DATETIME_1 = make_aware(
    datetime.datetime.strptime('2016-07-15 00:00:00', '%Y-%m-%d %H:%M:%S'))
MOCK_CSV_DATETIME_2 = make_aware(
    datetime.datetime.strptime('2016-07-15 00:30:00', '%Y-%m-%d %H:%M:%S'))
MOCK_CSV_DATETIME_3 = make_aware(
    datetime.datetime.strptime('2016-07-15 01:00:00', '%Y-%m-%d %H:%M:%S'))
MOCK_CSV_DATETIME_4 = make_aware(
    datetime.datetime.strptime('2016-07-15 01:30:00', '%Y-%m-%d %H:%M:%S'))

MOCK_CSV_DATA = {
    MOCK_USER_ID_1: {
        MOCK_CSV_DATETIME_1: 39.0,
        MOCK_CSV_DATETIME_2: 147.0,
        MOCK_CSV_DATETIME_3: 134.0,
        MOCK_CSV_DATETIME_4: 131.0,
    },
    MOCK_USER_ID_2: {
        MOCK_CSV_DATETIME_1: 378.0,
        MOCK_CSV_DATETIME_2: 341.0,
        MOCK_CSV_DATETIME_3: 317.0,
        MOCK_CSV_DATETIME_4: 292.0,
    },
    MOCK_USER_ID_3: {
        MOCK_CSV_DATETIME_1: 456.0,
        MOCK_CSV_DATETIME_2: 369.0,
        MOCK_CSV_DATETIME_3: 310.0,
        MOCK_CSV_DATETIME_4: 253.0,
    }
}


def mock_get_dup_user_data():
    return os.path.join(MOCK_DUP_DATA_DIR, MOCK_USER_DATA_FILE)


def mock_get_non_dup_user_data():
    return os.path.join(MOCK_NON_DUP_DATA_DIR, MOCK_USER_DATA_FILE)


def mock_get_dup_consumption_data_list():
    data_dir = os.path.join(MOCK_DUP_DATA_DIR, MOCK_CONSUM_DATA_DIR)

    return [
        os.path.abspath(os.path.join(data_dir, f)) for f in listdir(
            data_dir
        ) if isfile(
            join(data_dir, f)
        )
    ]


def mock_get_non_dup_consumption_data_list():
    data_dir = os.path.join(MOCK_NON_DUP_DATA_DIR, MOCK_CONSUM_DATA_DIR)

    return [
        os.path.abspath(os.path.join(data_dir, f)) for f in listdir(
            data_dir
        ) if isfile(
            join(data_dir, f)
        )
    ]


def mock_get_valid_result_dir():
    return os.path.join(MOCK_VALIDATION_DIR, 'test')


def mock_get_duplicatipm_result_dirname():
    return MOCK_DUP_RESULT_DIR_NAME


def delete_test_validation_result_files():
    try:
        test_result_dir = mock_get_valid_result_dir()
        shutil.rmtree(test_result_dir)
    except FileNotFoundError:
        pass


def get_module(name):
    if name in sys.modules:
        del sys.modules[name]

    mod = importlib.import_module(name)
    sys.modules[name] = mod

    return mod


def set_mock_data(import_mod, is_user_dup, is_consum_dup):
    if is_user_dup:
        import_mod.Command.get_user_data = MagicMock(
            return_value=mock_get_dup_user_data()
        )
    else:
        import_mod.Command.get_user_data = MagicMock(
            return_value=mock_get_non_dup_user_data()
        )
    if is_consum_dup:
        import_mod.Command.get_consumption_data_list = MagicMock(
            return_value=mock_get_dup_consumption_data_list()
        )
    else:
        import_mod.Command.get_consumption_data_list = MagicMock(
            return_value=mock_get_non_dup_consumption_data_list()
        )
    import_mod.Command.get_valid_result_dir = MagicMock(
        return_value=mock_get_valid_result_dir()
    )
    import_mod.Command.get_duplicatipm_result_dirname = MagicMock(
        return_value=mock_get_duplicatipm_result_dirname()
    )


class CommandValidationTestcase(TransactionTestCase):
    databases = '__all__'
    import_mod = None

    def setUp(self):
        delete_test_validation_result_files()
        self.import_mod = get_module(import_mod_path)

    def tearDown(self):
        delete_test_validation_result_files()

    def check_duplication_result_file(self, filepath, record_type):
        if record_type == 'user':
            dup_row_num_list = ['1', '2']
        if record_type == 'consumption':
            dup_row_num_list = ['2', '3']

        with open(filepath) as file:
            reader = csv.reader(file)
            data = list(reader)
            # only one record
            self.assertEqual(len(data), 1)
            # NOTICE: element order does not matter
            self.assertCountEqual(data[0], dup_row_num_list)

    def test_handle__validation_yes__duplication_found_in_user(self):
        set_mock_data(
            import_mod=self.import_mod,
            is_user_dup=True,
            is_consum_dup=True
        )
        command = self.import_mod.Command()
        # execute
        with self.assertRaises(Exception):
            command.handle(
                validation='yes',
                mode=self.import_mod.MODE_CHOICE_SKIP
            )
        # check if user is not created (rollbacked)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_1)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_2)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_3)

        # check if validation result files are created in directory
        dup_result_dir = os.path.join(
            mock_get_valid_result_dir(),
            mock_get_duplicatipm_result_dirname()
        )
        dup_file_list = listdir(dup_result_dir)
        self.assertEqual(len(dup_file_list), 4)
        self.assertTrue(MOCK_USER_DATA_FILE in dup_file_list)

        user_1_file = '{}.csv'.format(MOCK_USER_ID_1)
        user_2_file = '{}.csv'.format(MOCK_USER_ID_2)
        user_3_file = '{}.csv'.format(MOCK_USER_ID_3)
        self.assertTrue(user_1_file in dup_file_list)
        self.assertTrue(user_2_file in dup_file_list)
        self.assertTrue(user_3_file in dup_file_list)

        self.check_duplication_result_file(
            os.path.join(dup_result_dir, MOCK_USER_DATA_FILE),
            'user'
        )
        self.check_duplication_result_file(
            os.path.join(dup_result_dir, user_1_file),
            'consumption'
        )
        self.check_duplication_result_file(
            os.path.join(dup_result_dir, user_2_file),
            'consumption'
        )
        self.check_duplication_result_file(
            os.path.join(dup_result_dir, user_3_file),
            'consumption'
        )

    def test_handle__validation_yes__duplication_found_in_cunsumption(self):
        set_mock_data(
            import_mod=self.import_mod,
            is_user_dup=False,
            is_consum_dup=True
        )

        command = self.import_mod.Command()
        # execute
        with self.assertRaises(Exception):
            command.handle(
                validation='yes',
                mode=self.import_mod.MODE_CHOICE_SKIP
            )
        # check if user is not created (rollbacked)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_1)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_2)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_3)

        # check if validation result files are created in directory
        dup_result_dir = os.path.join(
            mock_get_valid_result_dir(),
            mock_get_duplicatipm_result_dirname()
        )
        dup_file_list = listdir(dup_result_dir)
        self.assertEqual(len(dup_file_list), 3)
        user_1_file = '{}.csv'.format(MOCK_USER_ID_1)
        user_2_file = '{}.csv'.format(MOCK_USER_ID_2)
        user_3_file = '{}.csv'.format(MOCK_USER_ID_3)
        self.assertTrue(user_1_file in dup_file_list)
        self.assertTrue(user_2_file in dup_file_list)
        self.assertTrue(user_3_file in dup_file_list)

        self.check_duplication_result_file(
            os.path.join(dup_result_dir, user_1_file),
            'consumption'
        )
        self.check_duplication_result_file(
            os.path.join(dup_result_dir, user_2_file),
            'consumption'
        )
        self.check_duplication_result_file(
            os.path.join(dup_result_dir, user_3_file),
            'consumption'
        )

    def test_handle__validation_yes__duplication_not_found(self):
        set_mock_data(
            import_mod=self.import_mod,
            is_user_dup=False,
            is_consum_dup=False
        )
        command = self.import_mod.Command()
        # execute
        command.handle(
            validation='yes',
            mode=self.import_mod.MODE_CHOICE_SKIP  # For importing, skip dup.
        )
        # check if user data and consumption created correctly
        user_1 = User.objects.get(id=MOCK_USER_ID_1)
        self.assertEqual(user_1.area, 'a1')
        self.assertEqual(user_1.tariff, 't1')
        consum_1 = Consumption.objects.filter(
            user_id=user_1).order_by('datetime')

        self.assertEqual(len(consum_1), 4)
        self.assertEqual(consum_1[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_1[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_1[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_1[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_2])
        self.assertEqual(consum_1[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_1[2].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_3])
        self.assertEqual(consum_1[3].datetime, MOCK_CSV_DATETIME_4)
        self.assertEqual(
            consum_1[3].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_4])

        user_2 = User.objects.get(id=MOCK_USER_ID_2)
        self.assertEqual(user_2.area, 'a2')
        self.assertEqual(user_2.tariff, 't2')
        consum_2 = Consumption.objects.filter(
            user_id=user_2).order_by('datetime')

        self.assertEqual(len(consum_2), 4)
        self.assertEqual(consum_2[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_2[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_2[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_2[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_2])
        self.assertEqual(consum_2[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_2[2].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_3])
        self.assertEqual(consum_2[3].datetime, MOCK_CSV_DATETIME_4)
        self.assertEqual(
            consum_2[3].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_4])

        user_3 = User.objects.get(id=MOCK_USER_ID_3)
        self.assertEqual(user_3.area, 'a3')
        self.assertEqual(user_3.tariff, 't3')
        consum_3 = Consumption.objects.filter(
            user_id=user_3).order_by('datetime')

        self.assertEqual(len(consum_3), 4)
        self.assertEqual(consum_3[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_3[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_3[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_3[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_2])
        self.assertEqual(consum_3[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_3[2].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_3])
        self.assertEqual(consum_3[3].datetime, MOCK_CSV_DATETIME_4)
        self.assertEqual(
            consum_3[3].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_4])

        # check if file is not created in directory
        dup_result_dir = os.path.join(
            mock_get_valid_result_dir(),
            mock_get_duplicatipm_result_dirname()
        )
        dup_file_list = listdir(dup_result_dir)
        self.assertEqual(len(dup_file_list), 0)


class CommandModeTestcase(TransactionTestCase):
    databases = '__all__'
    import_mod = None

    def setUp(self):
        delete_test_validation_result_files()
        self.import_mod = get_module(import_mod_path)

    def tearDown(self):
        delete_test_validation_result_files()

    def test_handle__mode_None(self):
        set_mock_data(
            import_mod=self.import_mod,
            is_user_dup=True,
            is_consum_dup=True
        )
        command = self.import_mod.Command()
        # execute
        with self.assertRaises(Exception):
            command.handle(
                validation='no',
                mode=None  # Not pass param
            )
        # check if user is not created
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_1)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_2)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_3)

    def test_handle__mode_skip__duplication_found_in_user(self):
        set_mock_data(
            import_mod=self.import_mod,
            is_user_dup=True,
            is_consum_dup=True
        )
        command = self.import_mod.Command()
        # execute
        with self.assertRaises(User.DoesNotExist):
            command.handle(
                validation='no',
                mode=self.import_mod.MODE_CHOICE_SKIP
            )
        # check if user is not created (rollbacked)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_1)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_2)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_3)

    def test_handle__mode_skip__duplication_found_in_consumption(self):
        set_mock_data(
            import_mod=self.import_mod,
            is_user_dup=False,
            is_consum_dup=True
        )
        command = self.import_mod.Command()
        # execute
        command.handle(
            validation='no',
            mode=self.import_mod.MODE_CHOICE_SKIP
        )
        # check if user data and consumption created correctly
        user_1 = User.objects.get(id=MOCK_USER_ID_1)
        self.assertEqual(user_1.area, 'a1')
        self.assertEqual(user_1.tariff, 't1')
        consum_1 = Consumption.objects.filter(
            user_id=user_1).order_by('datetime')
        # only 2 data was imported
        self.assertEqual(len(consum_1), 2)

        self.assertEqual(consum_1[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_1[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_1[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_1[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_2])

        user_2 = User.objects.get(id=MOCK_USER_ID_2)
        self.assertEqual(user_2.area, 'a2')
        self.assertEqual(user_2.tariff, 't2')
        consum_2 = Consumption.objects.filter(
            user_id=user_2).order_by('datetime')
        # only 2 data was imported
        self.assertEqual(len(consum_2), 2)
        self.assertEqual(consum_2[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_2[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_2[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_2[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_2])

        user_3 = User.objects.get(id=MOCK_USER_ID_3)
        self.assertEqual(user_3.area, 'a3')
        self.assertEqual(user_3.tariff, 't3')
        consum_3 = Consumption.objects.filter(
            user_id=user_3).order_by('datetime')
        # only 2 data was imported
        self.assertEqual(len(consum_3), 2)
        self.assertEqual(consum_3[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_3[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_3[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_3[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_2])

    def test_handle__mode_sum__duplication_found_in_user(self):
        set_mock_data(
            import_mod=self.import_mod,
            is_user_dup=True,
            is_consum_dup=False
        )
        command = self.import_mod.Command()
        # execute
        with self.assertRaises(Exception):
            command.handle(
                validation='no',
                mode=self.import_mod.MODE_CHOICE_SUM
            )

    def test_handle__mode_sum__duplication_found_in_consumption(self):
        set_mock_data(
            import_mod=self.import_mod,
            is_user_dup=False,
            is_consum_dup=True
        )
        command = self.import_mod.Command()
        # execute
        command.handle(
            validation='no',
            mode=self.import_mod.MODE_CHOICE_SUM
        )
        # check if user data and sum consumption created correctly
        user_1 = User.objects.get(id=MOCK_USER_ID_1)
        self.assertEqual(user_1.area, 'a1')
        self.assertEqual(user_1.tariff, 't1')
        consum_1 = Consumption.objects.filter(
            user_id=user_1).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_1), 3)
        self.assertEqual(consum_1[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_1[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_1[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_1[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_2])
        # imported as sum value
        sum_1 = MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_3] +\
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_4]
        self.assertEqual(consum_1[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(consum_1[2].consumption, sum_1)

        user_2 = User.objects.get(id=MOCK_USER_ID_2)
        self.assertEqual(user_2.area, 'a2')
        self.assertEqual(user_2.tariff, 't2')
        consum_2 = Consumption.objects.filter(
            user_id=user_2).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_2), 3)
        self.assertEqual(consum_2[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_2[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_2[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_2[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_2])
        # imported as sum value
        sum_2 = MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_3] +\
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_4]
        self.assertEqual(consum_2[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(consum_2[2].consumption, sum_2)

        user_3 = User.objects.get(id=MOCK_USER_ID_3)
        self.assertEqual(user_3.area, 'a3')
        self.assertEqual(user_3.tariff, 't3')
        consum_3 = Consumption.objects.filter(
            user_id=user_3).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_3), 3)
        self.assertEqual(consum_3[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_3[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_3[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_3[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_2])
        # imported as sum value
        sum_3 = MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_3] +\
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_4]
        self.assertEqual(consum_3[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(consum_3[2].consumption, sum_3)

    def test_handle__mode_first__duplication_found_in_consumption(self):
        set_mock_data(
            import_mod=self.import_mod,
            is_user_dup=False,
            is_consum_dup=True
        )
        command = self.import_mod.Command()
        # execute
        command.handle(
            validation='no',
            mode=self.import_mod.MODE_CHOICE_FIRST
        )
        # check if user data and consumption created correctly
        user_1 = User.objects.get(id=MOCK_USER_ID_1)
        self.assertEqual(user_1.area, 'a1')
        self.assertEqual(user_1.tariff, 't1')
        consum_1 = Consumption.objects.filter(
            user_id=user_1).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_1), 3)

        self.assertEqual(consum_1[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_1[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_1[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_1[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_2])
        # first one is imported
        self.assertEqual(consum_1[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_1[2].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_3])

        user_2 = User.objects.get(id=MOCK_USER_ID_2)
        self.assertEqual(user_2.area, 'a2')
        self.assertEqual(user_2.tariff, 't2')
        consum_2 = Consumption.objects.filter(
            user_id=user_2).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_2), 3)
        self.assertEqual(consum_2[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_2[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_2[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_2[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_2])
        # first one is imported
        self.assertEqual(consum_2[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_2[2].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_3])

        user_3 = User.objects.get(id=MOCK_USER_ID_3)
        self.assertEqual(user_3.area, 'a3')
        self.assertEqual(user_3.tariff, 't3')
        consum_3 = Consumption.objects.filter(
            user_id=user_3).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_3), 3)
        self.assertEqual(consum_3[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_3[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_3[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_3[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_2])
        # first one is imported
        self.assertEqual(consum_3[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_3[2].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_3])

    def test_handle__mode_last__duplication_found_in_consumption(self):
        set_mock_data(
            import_mod=self.import_mod,
            is_user_dup=False,
            is_consum_dup=True
        )
        command = self.import_mod.Command()
        # execute
        command.handle(
            validation='no',
            mode=self.import_mod.MODE_CHOICE_LAST
        )
        # check if user data and consumption created correctly
        user_1 = User.objects.get(id=MOCK_USER_ID_1)
        self.assertEqual(user_1.area, 'a1')
        self.assertEqual(user_1.tariff, 't1')
        consum_1 = Consumption.objects.filter(
            user_id=user_1).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_1), 3)

        self.assertEqual(consum_1[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_1[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_1[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_1[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_2])
        # last one is imported
        self.assertEqual(consum_1[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_1[2].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_4])

        user_2 = User.objects.get(id=MOCK_USER_ID_2)
        self.assertEqual(user_2.area, 'a2')
        self.assertEqual(user_2.tariff, 't2')
        consum_2 = Consumption.objects.filter(
            user_id=user_2).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_2), 3)
        self.assertEqual(consum_2[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_2[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_2[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_2[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_2])
        # last one is imported
        self.assertEqual(consum_2[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_2[2].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_4])

        user_3 = User.objects.get(id=MOCK_USER_ID_3)
        self.assertEqual(user_3.area, 'a3')
        self.assertEqual(user_3.tariff, 't3')
        consum_3 = Consumption.objects.filter(
            user_id=user_3).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_3), 3)
        self.assertEqual(consum_3[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_3[0].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_3[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_3[1].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_2])
        # last one is imported
        self.assertEqual(consum_3[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_3[2].consumption,
            MOCK_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_4])

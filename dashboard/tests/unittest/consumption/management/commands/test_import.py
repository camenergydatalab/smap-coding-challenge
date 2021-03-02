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
MOCK_DUP_FILE_HEADER = ['duplicated index']

# Definition of Mock user info

MOCK_USER_ID_1 = 1111
MOCK_USER_ID_2 = 2222
MOCK_USER_ID_3 = 3333

MOCK_UR_CSV_DATA = {
    MOCK_USER_ID_1: {
        'area': 'a1',
        'tariff': "t1"
    },
    MOCK_USER_ID_2: {
        'area': 'a2',
        'tariff': "t2"
    },
    MOCK_USER_ID_3: {
        'area': 'a3',
        'tariff': "t3"
    },
}

# Definition of Mock Cousumption info
MOCK_CSV_DATETIME_1 = make_aware(
    datetime.datetime.strptime('2016-07-15 00:00:00', '%Y-%m-%d %H:%M:%S'))
MOCK_CSV_DATETIME_2 = make_aware(
    datetime.datetime.strptime('2016-07-15 00:30:00', '%Y-%m-%d %H:%M:%S'))
MOCK_CSV_DATETIME_3 = make_aware(
    datetime.datetime.strptime('2016-07-15 01:00:00', '%Y-%m-%d %H:%M:%S'))
MOCK_CSV_DATETIME_4 = make_aware(
    datetime.datetime.strptime('2016-07-15 01:30:00', '%Y-%m-%d %H:%M:%S'))

MOCK_CM_CSV_DATA = {
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


def mock_get_dup_user_data_path():
    """mock for "get_user_data_path" function

    Returns:
        str: diplicated mock user data file path
    """
    return os.path.join(MOCK_DUP_DATA_DIR, MOCK_USER_DATA_FILE)


def mock_get_non_dup_user_data_path():
    """mock for "get_user_data_path" function

    Returns:
        str: valid mock user data file path
    """
    return os.path.join(MOCK_NON_DUP_DATA_DIR, MOCK_USER_DATA_FILE)


def mock_get_dup_consum_data_path_list():
    """mock for "get_consumption_data_path_list" function

    Returns:
        list[str]: list of diplicated mock consumption data file path
    """
    data_dir = os.path.join(MOCK_DUP_DATA_DIR, MOCK_CONSUM_DATA_DIR)

    return [
        os.path.abspath(os.path.join(data_dir, f)) for f in listdir(
            data_dir
        ) if isfile(
            join(data_dir, f)
        )
    ]


def mock_get_non_dup_consum_data_path_list():
    """mock for "get_consumption_data_path_list" function

    Returns:
        list[str]: list of valid mock consumption data file path
    """
    data_dir = os.path.join(MOCK_NON_DUP_DATA_DIR, MOCK_CONSUM_DATA_DIR)

    return [
        os.path.abspath(os.path.join(data_dir, f)) for f in listdir(
            data_dir
        ) if isfile(
            join(data_dir, f)
        )
    ]


def mock_get_valid_result_dir_path():
    """mock for "get_valid_result_dir_path" function

    Returns:
        str: mock file path to save validation result
    """
    return os.path.join(MOCK_VALIDATION_DIR, 'test')


def mock_get_duplicatipm_result_dirname():
    """mock for "get_duplicatipm_result_dirname" function

    Returns:
        str: mock folder name for duplication result
    """
    return MOCK_DUP_RESULT_DIR_NAME


def mock_get_dup_result_file_header():
    """mock for "get_dup_result_file_header" function

    Returns:
        str: mock header name of duplicated result recording file
    """
    return MOCK_DUP_FILE_HEADER


def delete_test_validation_result_files():
    """delete mock validation result files

    Delete result files used in tests.

    """
    try:
        test_result_dir = mock_get_valid_result_dir_path()
        shutil.rmtree(test_result_dir)
    except FileNotFoundError:
        pass


def reset_module(path):
    """reset module

    Reset module.
    Use if you want clean module for each tests.

    Args:
        path (str): module path to import
    """
    if path in sys.modules:
        del sys.modules[path]

    module = importlib.import_module(path)
    sys.modules[path] = module

    return module


def set_mock_data(import_mod, is_user_dup, is_consum_dup):
    """set mock data

    Set mock data.

    Args:
        import_mod (Module): import.py as Module object
    """
    if is_user_dup:
        import_mod.Command.get_user_data_path = MagicMock(
            return_value=mock_get_dup_user_data_path()
        )
    else:
        import_mod.Command.get_user_data_path = MagicMock(
            return_value=mock_get_non_dup_user_data_path()
        )
    if is_consum_dup:
        import_mod.Command.get_consumption_data_path_list = MagicMock(
            return_value=mock_get_dup_consum_data_path_list()
        )
    else:
        import_mod.Command.get_consumption_data_path_list = MagicMock(
            return_value=mock_get_non_dup_consum_data_path_list()
        )
    import_mod.Command.get_valid_result_dir_path = MagicMock(
        return_value=mock_get_valid_result_dir_path()
    )
    import_mod.Command.get_duplicatipm_result_dirname = MagicMock(
        return_value=mock_get_duplicatipm_result_dirname()
    )
    import_mod.Command.get_dup_result_file_header = MagicMock(
        return_value=mock_get_dup_result_file_header()
    )


class CommandValidationTestcase(TransactionTestCase):
    """Test for Command class with validation parameter

    Attributes:
        import_mod (Module): Module object of import.py
    """
    import_mod = None

    def setUp(self):
        delete_test_validation_result_files()
        self.import_mod = reset_module(import_mod_path)

    def tearDown(self):
        self.import_mod = None
        delete_test_validation_result_files()

    def check_duplication_result_file(self, filepath, record_type):
        """check duplication result file

        NOTICE: duplicated culumn is fixed.

        Args:
            filepath (str): file path
            record_type (str): user or consumption
        """
        if record_type == 'user':
            dup_row_num_list = ['1', '2']
        if record_type == 'consumption':
            dup_row_num_list = ['2', '3']

        with open(filepath) as file:
            reader = csv.reader(file)
            data = list(reader)
            # only one record
            self.assertEqual(len(data), 2)
            # NOTICE: element order does not matter
            self.assertCountEqual(data[0], mock_get_dup_result_file_header())
            self.assertCountEqual(data[1], dup_row_num_list)

    def check_user_is_not_created(self):
        """check user is not created

        NOTICE: user data is fixed.
        """
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_1)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_2)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_3)

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
        self.check_user_is_not_created()

        # check if validation result files are created in directory
        dup_result_dir = os.path.join(
            mock_get_valid_result_dir_path(),
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
        self.check_user_is_not_created()

        # check if validation result files are created in directory
        dup_result_dir = os.path.join(
            mock_get_valid_result_dir_path(),
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
        self.assertEqual(user_1.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_1]['area'])
        self.assertEqual(
            user_1.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_1]['tariff'])
        consum_1 = Consumption.objects.filter(
            user_id=user_1).order_by('datetime')

        self.assertEqual(len(consum_1), 4)
        self.assertEqual(consum_1[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_1[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_1[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_1[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_2])
        self.assertEqual(consum_1[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_1[2].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_3])
        self.assertEqual(consum_1[3].datetime, MOCK_CSV_DATETIME_4)
        self.assertEqual(
            consum_1[3].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_4])

        user_2 = User.objects.get(id=MOCK_USER_ID_2)
        self.assertEqual(user_2.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_2]['area'])
        self.assertEqual(
            user_2.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_2]['tariff'])
        consum_2 = Consumption.objects.filter(
            user_id=user_2).order_by('datetime')

        self.assertEqual(len(consum_2), 4)
        self.assertEqual(consum_2[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_2[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_2[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_2[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_2])
        self.assertEqual(consum_2[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_2[2].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_3])
        self.assertEqual(consum_2[3].datetime, MOCK_CSV_DATETIME_4)
        self.assertEqual(
            consum_2[3].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_4])

        user_3 = User.objects.get(id=MOCK_USER_ID_3)
        self.assertEqual(user_3.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_3]['area'])
        self.assertEqual(
            user_3.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_3]['tariff'])
        consum_3 = Consumption.objects.filter(
            user_id=user_3).order_by('datetime')

        self.assertEqual(len(consum_3), 4)
        self.assertEqual(consum_3[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_3[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_3[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_3[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_2])
        self.assertEqual(consum_3[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_3[2].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_3])
        self.assertEqual(consum_3[3].datetime, MOCK_CSV_DATETIME_4)
        self.assertEqual(
            consum_3[3].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_4])

        # check if file is not created in directory
        dup_result_dir = os.path.join(
            mock_get_valid_result_dir_path(),
            mock_get_duplicatipm_result_dirname()
        )
        dup_file_list = listdir(dup_result_dir)
        self.assertEqual(len(dup_file_list), 0)


class CommandModeTestcase(TransactionTestCase):
    """Test for Command class with mode parameter

    Attributes:
        import_mod (Module): Module object of import.py
    """
    import_mod = None

    def setUp(self):
        delete_test_validation_result_files()
        self.import_mod = reset_module(import_mod_path)

    def tearDown(self):
        self.import_mod = None
        delete_test_validation_result_files()

    def check_user_is_not_created(self):
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_1)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_2)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=MOCK_USER_ID_3)

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
        self.check_user_is_not_created()

    def test_handle__mode_skip__duplication_found_in_user(self):
        set_mock_data(
            import_mod=self.import_mod,
            is_user_dup=True,
            is_consum_dup=True
        )
        command = self.import_mod.Command()
        # execute
        command.handle(
            validation='no',
            mode=self.import_mod.MODE_CHOICE_SKIP
        )
        # check if user is not created (rollbacked)
        self.check_user_is_not_created()

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
        self.assertEqual(user_1.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_1]['area'])
        self.assertEqual(
            user_1.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_1]['tariff'])
        consum_1 = Consumption.objects.filter(
            user_id=user_1).order_by('datetime')
        # only 2 data was imported
        self.assertEqual(len(consum_1), 2)

        self.assertEqual(consum_1[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_1[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_1[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_1[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_2])

        user_2 = User.objects.get(id=MOCK_USER_ID_2)
        self.assertEqual(user_2.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_2]['area'])
        self.assertEqual(
            user_2.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_2]['tariff'])
        consum_2 = Consumption.objects.filter(
            user_id=user_2).order_by('datetime')
        # only 2 data was imported
        self.assertEqual(len(consum_2), 2)
        self.assertEqual(consum_2[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_2[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_2[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_2[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_2])

        user_3 = User.objects.get(id=MOCK_USER_ID_3)
        self.assertEqual(user_3.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_3]['area'])
        self.assertEqual(
            user_3.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_3]['tariff'])
        consum_3 = Consumption.objects.filter(
            user_id=user_3).order_by('datetime')
        # only 2 data was imported
        self.assertEqual(len(consum_3), 2)
        self.assertEqual(consum_3[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_3[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_3[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_3[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_2])

    def test_handle__mode_sum__duplication_found_in_user(self):
        set_mock_data(
            import_mod=self.import_mod,
            is_user_dup=True,
            is_consum_dup=False
        )
        command = self.import_mod.Command()
        # execute
        command.handle(
            validation='no',
            mode=self.import_mod.MODE_CHOICE_SUM
        )
        # check if user is not created (rollbacked)
        self.check_user_is_not_created()

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
        self.assertEqual(user_1.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_1]['area'])
        self.assertEqual(
            user_1.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_1]['tariff'])
        consum_1 = Consumption.objects.filter(
            user_id=user_1).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_1), 3)
        self.assertEqual(consum_1[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_1[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_1[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_1[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_2])
        # imported as sum value
        sum_1 = MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_3] +\
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_4]
        self.assertEqual(consum_1[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(consum_1[2].consumption, sum_1)

        user_2 = User.objects.get(id=MOCK_USER_ID_2)
        self.assertEqual(user_2.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_2]['area'])
        self.assertEqual(
            user_2.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_2]['tariff'])
        consum_2 = Consumption.objects.filter(
            user_id=user_2).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_2), 3)
        self.assertEqual(consum_2[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_2[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_2[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_2[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_2])
        # imported as sum value
        sum_2 = MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_3] +\
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_4]
        self.assertEqual(consum_2[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(consum_2[2].consumption, sum_2)

        user_3 = User.objects.get(id=MOCK_USER_ID_3)
        self.assertEqual(user_3.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_3]['area'])
        self.assertEqual(
            user_3.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_3]['tariff'])
        consum_3 = Consumption.objects.filter(
            user_id=user_3).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_3), 3)
        self.assertEqual(consum_3[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_3[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_3[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_3[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_2])
        # imported as sum value
        sum_3 = MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_3] +\
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_4]
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
        self.assertEqual(user_1.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_1]['area'])
        self.assertEqual(
            user_1.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_1]['tariff'])
        consum_1 = Consumption.objects.filter(
            user_id=user_1).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_1), 3)

        self.assertEqual(consum_1[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_1[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_1[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_1[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_2])
        # first one is imported
        self.assertEqual(consum_1[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_1[2].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_3])

        user_2 = User.objects.get(id=MOCK_USER_ID_2)
        self.assertEqual(user_2.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_2]['area'])
        self.assertEqual(
            user_2.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_2]['tariff'])
        consum_2 = Consumption.objects.filter(
            user_id=user_2).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_2), 3)
        self.assertEqual(consum_2[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_2[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_2[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_2[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_2])
        # first one is imported
        self.assertEqual(consum_2[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_2[2].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_3])

        user_3 = User.objects.get(id=MOCK_USER_ID_3)
        self.assertEqual(user_3.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_3]['area'])
        self.assertEqual(
            user_3.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_3]['tariff'])
        consum_3 = Consumption.objects.filter(
            user_id=user_3).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_3), 3)
        self.assertEqual(consum_3[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_3[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_3[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_3[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_2])
        # first one is imported
        self.assertEqual(consum_3[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_3[2].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_3])

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
        self.assertEqual(user_1.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_1]['area'])
        self.assertEqual(
            user_1.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_1]['tariff'])
        consum_1 = Consumption.objects.filter(
            user_id=user_1).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_1), 3)

        self.assertEqual(consum_1[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_1[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_1[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_1[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_2])
        # last one is imported
        self.assertEqual(consum_1[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_1[2].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_1][MOCK_CSV_DATETIME_4])

        user_2 = User.objects.get(id=MOCK_USER_ID_2)
        self.assertEqual(user_2.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_2]['area'])
        self.assertEqual(
            user_2.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_2]['tariff'])
        consum_2 = Consumption.objects.filter(
            user_id=user_2).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_2), 3)
        self.assertEqual(consum_2[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_2[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_2[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_2[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_2])
        # last one is imported
        self.assertEqual(consum_2[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_2[2].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_2][MOCK_CSV_DATETIME_4])

        user_3 = User.objects.get(id=MOCK_USER_ID_3)
        self.assertEqual(user_3.area, MOCK_UR_CSV_DATA[MOCK_USER_ID_3]['area'])
        self.assertEqual(
            user_3.tariff, MOCK_UR_CSV_DATA[MOCK_USER_ID_3]['tariff'])
        consum_3 = Consumption.objects.filter(
            user_id=user_3).order_by('datetime')
        # only 3 data was imported
        self.assertEqual(len(consum_3), 3)
        self.assertEqual(consum_3[0].datetime, MOCK_CSV_DATETIME_1)
        self.assertEqual(
            consum_3[0].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_1])
        self.assertEqual(consum_3[1].datetime, MOCK_CSV_DATETIME_2)
        self.assertEqual(
            consum_3[1].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_2])
        # last one is imported
        self.assertEqual(consum_3[2].datetime, MOCK_CSV_DATETIME_3)
        self.assertEqual(
            consum_3[2].consumption,
            MOCK_CM_CSV_DATA[MOCK_USER_ID_3][MOCK_CSV_DATETIME_4])

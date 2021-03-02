# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import statistics
from functools import reduce
from unittest.mock import MagicMock, patch

from django.test import TransactionTestCase
from tests import test_fixtures

from consumption.services import (
    create_chart_data,
    create_table_data,
    get_user_avg_consum,
    create_user_chart_data,
)
from consumption.models import Consumption, User


# user data
ALL_USER_DATA_LIST = [
    test_fixtures.USER_DATA_1, test_fixtures.USER_DATA_2,
    test_fixtures.USER_DATA_3
]

# consumption data group by user
USER_1_CONSUM_LIST = [
    test_fixtures.CONSUM_DATA_USER_1_1, test_fixtures.CONSUM_DATA_USER_1_2,
    test_fixtures.CONSUM_DATA_USER_1_3
]
USER_2_CONSUM_LIST = [
    test_fixtures.CONSUM_DATA_USER_2_1, test_fixtures.CONSUM_DATA_USER_2_2,
    test_fixtures.CONSUM_DATA_USER_2_3
]
USER_3_CONSUM_LIST = [
    test_fixtures.CONSUM_DATA_USER_3_1, test_fixtures.CONSUM_DATA_USER_3_2,
    test_fixtures.CONSUM_DATA_USER_3_3
]
# flatten list of each user's consumption data
ALL_CONSUM_DATA_LIST = reduce(
    lambda a, b: a + b,
    [USER_1_CONSUM_LIST, USER_2_CONSUM_LIST, USER_3_CONSUM_LIST]
)

# consumption data group by datetime
DATETIME_1_CONSUM_LIST = [
    test_fixtures.CONSUM_DATA_USER_1_1, test_fixtures.CONSUM_DATA_USER_2_1,
    test_fixtures.CONSUM_DATA_USER_3_1
]
DATETIME_2_CONSUM_LIST = [
    test_fixtures.CONSUM_DATA_USER_1_2, test_fixtures.CONSUM_DATA_USER_2_2,
    test_fixtures.CONSUM_DATA_USER_3_2
]
DATETIME_3_CONSUM_LIST = [
    test_fixtures.CONSUM_DATA_USER_1_3, test_fixtures.CONSUM_DATA_USER_2_3,
    test_fixtures.CONSUM_DATA_USER_3_3
]

# user's average value
MIN_AVG_VALUE = '100'
MAX_AVG_VALUE = '300'
MOCK_AVG_CUNSUM = {
    test_fixtures.USER_DATA_1['id']: MIN_AVG_VALUE,
    test_fixtures.USER_DATA_2['id']: '200',
    test_fixtures.USER_DATA_3['id']: MAX_AVG_VALUE,
}


def get_mock_average_consum(data_list):
    """get mock user's average consumption

    Caluculate average consumption from mock user data.

    Args:
        data_list (list[{
            'consumption': consumption value
        }])

    Returns:
        int: average consumption value
    """
    return statistics.mean(
        data['consumption'] for data in data_list
    )


def get_total_consum(data_list):
    """get mock user's total consumption

    Caluculate total consumption from mock user data.

    Args:
        data_list (
            list[
                {
                    'consumption': consumption value
                }
            ]
        )

    Returns:
        int: total consumption value
    """
    return sum([
        data['consumption'] for data in data_list
    ])


def mock_create_chart_data():
    """mock for "create_chart_data" function

    Returns: dict:
        {
            'labels': list[str], ...datetime labels for data,
            'total_data': list[str], ...total consumption data,
            'avg_data': list[str] ...average consumption dat
        }
    """
    labels = [
        test_fixtures.TEST_DATETIME_1.strftime("%Y-%m-%d %H:%M:%S"),
        test_fixtures.TEST_DATETIME_2.strftime("%Y-%m-%d %H:%M:%S"),
        test_fixtures.TEST_DATETIME_3.strftime("%Y-%m-%d %H:%M:%S"),
    ]
    total_data = [
        str(get_total_consum(DATETIME_1_CONSUM_LIST)),
        str(get_total_consum(DATETIME_2_CONSUM_LIST)),
        str(get_total_consum(DATETIME_3_CONSUM_LIST)),
    ]
    avg_data = [
        str(get_mock_average_consum(DATETIME_1_CONSUM_LIST)),
        str(get_mock_average_consum(DATETIME_2_CONSUM_LIST)),
        str(get_mock_average_consum(DATETIME_3_CONSUM_LIST)),
    ]

    return {
        'labels': labels,
        'total_data': total_data,
        'avg_data': avg_data
    }


def mock_create_table_data():
    """mock for "create_table_data" function

    Returns: dict:
        {
            'data': [{
                'id': int, ...user id
                'area': str, ...user area,
                'tariff': str, ...user tariff,
                'average': str, ...user's average consumption
            }],
            'min_value': int, ... minimum use's average consumption
            'max_value': int, ... maximum use's average consumption
        }
    """
    data = []
    for user in ALL_USER_DATA_LIST:
        data.append({
            'id': user['id'],
            'area': user['area'],
            'tariff': user['tariff'],
            'average': MOCK_AVG_CUNSUM[user['id']]
        })

    return data


def setup_mock_data():
    """set up mock data

    Create data for test.
    """
    for user_data in ALL_USER_DATA_LIST:
        test_fixtures.UserTestData.setUp(user_data)
    for consum_data in ALL_CONSUM_DATA_LIST:
        test_fixtures.ConsumptionTestData.setUp(consum_data)


class CreateChartDataTestcase(TransactionTestCase):
    """Test for "create_chart_data" function
    """
    def test_create_chart_data(self):
        setup_mock_data()
        expected = mock_create_chart_data()

        # execute
        result = create_chart_data()

        # key's count is 3
        self.assertEqual(3, len(result.keys()))
        self.assertEqual(expected['labels'], result['labels'])
        self.assertEqual(expected['total_data'], result['total_data'])
        self.assertEqual(expected['avg_data'], result['avg_data'])

    def test_create_chart_data__raise_does_not_exist(self):
        # execute
        with self.assertRaises(Consumption.DoesNotExist):
            create_chart_data()


class CreateTableDataTestcase(TransactionTestCase):
    """Test for "create_table_data" function
    """
    # mock get_user_avg_consum
    @patch(
        'consumption.services.get_user_avg_consum',
        MagicMock(return_value=MOCK_AVG_CUNSUM))
    def test_create_table_data(self):
        setup_mock_data()
        expected = mock_create_table_data()

        # execute
        result = create_table_data()

        # key's count is 3
        self.assertEqual(3, len(result.keys()))
        # NOTICE: element order does not matter
        self.assertCountEqual(expected, result['data'])
        self.assertEqual(MIN_AVG_VALUE, result['min_value'])
        self.assertEqual(MAX_AVG_VALUE, result['max_value'])

    # mock get_user_avg_consum
    @patch(
        'consumption.services.get_user_avg_consum',
        MagicMock(return_value=MOCK_AVG_CUNSUM))
    def test_create_table_data__raise_does_not_exist(self):
        # execute
        with self.assertRaises(User.DoesNotExist):
            create_table_data()


class GetUserAvgConsumTestcase(TransactionTestCase):
    """Test for "get_user_avg_consum" function
    """
    def test_get_user_avg_consum(self):
        setup_mock_data()
        expected = {
            test_fixtures.USER_DATA_1['id']: str(
                get_mock_average_consum(USER_1_CONSUM_LIST)),
            test_fixtures.USER_DATA_2['id']: str(
                get_mock_average_consum(USER_2_CONSUM_LIST)),
            test_fixtures.USER_DATA_3['id']: str(
                get_mock_average_consum(USER_3_CONSUM_LIST))
        }
        # execute
        result = get_user_avg_consum()

        self.assertDictEqual(expected, result)

    def test_get_user_avg_consum__raise_does_not_exist(self):
        # execute
        with self.assertRaises(Consumption.DoesNotExist):
            get_user_avg_consum()


class CreateUserChartDataTestcase(TransactionTestCase):
    """Test for "create_user_chart_data" function
    """
    def test_create_user_chart_data(self):
        setup_mock_data()
        expected_labels = []
        expected_data = []
        for data in USER_1_CONSUM_LIST:
            expected_labels.append(
                data['datetime'].strftime("%Y-%m-%d %H:%M:%S"))
            expected_data.append(
                '{}.0'.format(str(data['consumption'])))
        # execute
        result = create_user_chart_data(test_fixtures.USER_1)

        self.assertEqual(len(result.keys()), 2)
        self.assertListEqual(result['labels'], expected_labels)
        self.assertListEqual(result['data'], expected_data)

    def test_create_user_chart_data__raise_does_not_exist(self):
        # execute
        with self.assertRaises(User.DoesNotExist):
            create_user_chart_data(111111)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import statistics
from io import StringIO
from functools import reduce
from unittest.mock import MagicMock, patch

from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest

from django.test import TransactionTestCase
from tests import test_data

from consumption.views import (
    create_table_data,
    get_user_avg_consum,
    create_chart_data,
    summary,
)


# user data
ALL_USER_DATA_LIST = [
    test_data.USER_DATA_1, test_data.USER_DATA_2, test_data.USER_DATA_3
]

# consumption data group by user
USER_1_CONSUM_LIST = [
    test_data.CONSUM_DATA_USER_1_1, test_data.CONSUM_DATA_USER_1_2,
    test_data.CONSUM_DATA_USER_1_3
]
USER_2_CONSUM_LIST = [
    test_data.CONSUM_DATA_USER_2_1, test_data.CONSUM_DATA_USER_2_2,
    test_data.CONSUM_DATA_USER_2_3
]
USER_3_CONSUM_LIST = [
    test_data.CONSUM_DATA_USER_3_1, test_data.CONSUM_DATA_USER_3_2,
    test_data.CONSUM_DATA_USER_3_3
]
# flatten list of each user's consumption data
ALL_CONSUM_DATA_LIST = reduce(
    lambda a, b: a + b,
    [USER_1_CONSUM_LIST, USER_2_CONSUM_LIST, USER_3_CONSUM_LIST]
)

# consumption data group by datetime
DATETIME_1_CONSUM_LIST = [
    test_data.CONSUM_DATA_USER_1_1, test_data.CONSUM_DATA_USER_2_1,
    test_data.CONSUM_DATA_USER_3_1
]
DATETIME_2_CONSUM_LIST = [
    test_data.CONSUM_DATA_USER_1_2, test_data.CONSUM_DATA_USER_2_2,
    test_data.CONSUM_DATA_USER_3_2
]
DATETIME_3_CONSUM_LIST = [
    test_data.CONSUM_DATA_USER_1_3, test_data.CONSUM_DATA_USER_2_3,
    test_data.CONSUM_DATA_USER_3_3
]

# user's average value
MIN_AVG_VALUE = '100'
MAX_AVG_VALUE = '300'
MOCK_AVG_CUNSUM = {
    test_data.USER_DATA_1['id']: MIN_AVG_VALUE,
    test_data.USER_DATA_2['id']: '200',
    test_data.USER_DATA_3['id']: MAX_AVG_VALUE,
}


def get_average_consum(data_list):
    return statistics.mean(
        data['consumption'] for data in data_list
    )


def get_total_consum(data_list):
    return sum([
        data['consumption'] for data in data_list
    ])


def mock_create_chart_data():
    labels = [
        test_data.TEST_DATETIME_1.strftime("%Y-%m-%d %H:%M:%S"),
        test_data.TEST_DATETIME_2.strftime("%Y-%m-%d %H:%M:%S"),
        test_data.TEST_DATETIME_3.strftime("%Y-%m-%d %H:%M:%S"),
    ]
    total_data = [
        str(get_total_consum(DATETIME_1_CONSUM_LIST)),
        str(get_total_consum(DATETIME_2_CONSUM_LIST)),
        str(get_total_consum(DATETIME_3_CONSUM_LIST)),
    ]
    avg_data = [
        str(get_average_consum(DATETIME_1_CONSUM_LIST)),
        str(get_average_consum(DATETIME_2_CONSUM_LIST)),
        str(get_average_consum(DATETIME_3_CONSUM_LIST)),
    ]

    return {
        'labels': labels,
        'total_data': total_data,
        'avg_data': avg_data
    }


def mock_create_table_data():
    data = []
    for user in ALL_USER_DATA_LIST:
        data.append({
            'id': user['id'],
            'area': user['area'],
            'tariff': user['tariff'],
            'average': MOCK_AVG_CUNSUM[user['id']]
        })

    return data


class SummaryTestcase(TransactionTestCase):
    databases = '__all__'

    def setUp(self):
        for user_data in ALL_USER_DATA_LIST:
            test_data.UserTestData.setUp(user_data)
        for consum_data in ALL_CONSUM_DATA_LIST:
            test_data.ConsumptionTestData.setUp(consum_data)

    def test_create_chart_data(self):
        expected = mock_create_chart_data()

        # execute
        result = create_chart_data()

        # key's count is 3
        self.assertEqual(3, len(result.keys()))
        self.assertEqual(expected['labels'], result['labels'])
        self.assertEqual(expected['total_data'], result['total_data'])
        self.assertEqual(expected['avg_data'], result['avg_data'])

    # mock get_user_avg_consum
    @patch(
        'consumption.views.get_user_avg_consum',
        MagicMock(return_value=MOCK_AVG_CUNSUM))
    def test_create_table_data(self):
        expected = mock_create_table_data()

        # execute
        result = create_table_data()

        # key's count is 3
        self.assertEqual(3, len(result.keys()))
        # NOTICE: element order does not matter
        self.assertCountEqual(expected, result['data'])
        self.assertEqual(MIN_AVG_VALUE, result['min_value'])
        self.assertEqual(MAX_AVG_VALUE, result['max_value'])

    def test_get_user_avg_consum(self):
        expected = {
            test_data.USER_DATA_1['id']: str(
                get_average_consum(USER_1_CONSUM_LIST)),
            test_data.USER_DATA_2['id']: str(
                get_average_consum(USER_2_CONSUM_LIST)),
            test_data.USER_DATA_3['id']: str(
                get_average_consum(USER_3_CONSUM_LIST))
        }
        # execute
        result = get_user_avg_consum()

        self.assertDictEqual(expected, result)

    # mock get_user_avg_consum
    @patch(
        'consumption.views.create_chart_data',
        MagicMock(return_value=mock_create_chart_data()))
    @patch(
        'consumption.views.create_table_data',
        MagicMock(return_value=mock_create_table_data()))
    def test_summary(self):
        request = WSGIRequest(
            {
                'REQUEST_METHOD': 'GET',
                'PATH_INFO': '/',
                'wsgi.input': StringIO()
            }
        )
        expected_context = {
            'chart_data': mock_create_chart_data(),
            'table_data': mock_create_table_data()
        }
        expected = render(
            request, 'consumption/summary.html', expected_context)

        # execute
        result = summary(request)

        self.assertEqual(expected.content, result.content)

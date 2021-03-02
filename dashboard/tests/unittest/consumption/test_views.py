# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404
from django.shortcuts import render
from django.test import TransactionTestCase

from consumption.models import Consumption, User
from consumption.views import summary, detail

from tests import test_fixtures


MOCK_CHART_DATA = {
    'labels': 'mock label',
    'total_data': 'mock total_data',
    'avg_data': 'mock avg_data'
}

MOCK_TABLE_DATA = {
    'data': 'mock data',
    'min_value': 'mock min_value',
    'max_value': 'mock max_value'
}

MOCK_USER_CHART_DATA = {
    'labels': 'mock label',
    'data': 'mock data'
}


def mock_summary_request():
    """mock request for summary

    Returns:
        WSGIRequest: WSGIRequest object in summary path
    """
    return WSGIRequest(
        {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/',
            'wsgi.input': StringIO()
        }
    )


def mock_detail_request(user_id):
    """mock request for detail

    Args:
        user_id (int): user id

    Returns:
        WSGIRequest: WSGIRequest object in detail path
    """
    return WSGIRequest(
        {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/detail/{}'.format(user_id),
            'wsgi.input': StringIO()
        }
    )


class SummaryTestcase(TransactionTestCase):
    """Test for summary view
    """
    # mock create_chart_data and create_table_data
    @patch(
        'consumption.views.create_chart_data',
        MagicMock(return_value=MOCK_CHART_DATA))
    @patch(
        'consumption.views.create_table_data',
        MagicMock(return_value=MOCK_TABLE_DATA))
    def test_summary(self):
        request = mock_summary_request()
        expected_context = {
            'chart_data': {
                'labels': MOCK_CHART_DATA['labels'],
                'total_data': MOCK_CHART_DATA['total_data'],
                'avg_data': MOCK_CHART_DATA['avg_data']
            },
            'table_data': {
                'data': MOCK_TABLE_DATA['data'],
                'min_value': MOCK_TABLE_DATA['min_value'],
                'max_value': MOCK_TABLE_DATA['max_value']
            }
        }
        expected = render(
            request, 'consumption/summary.html', expected_context)

        # execute
        result = summary(request)

        self.assertEqual(expected.status_code, result.status_code)

    # raise error on create_chart_data
    @patch(
        'consumption.views.create_chart_data',
        MagicMock(side_effect=Consumption.DoesNotExist))
    @patch(
        'consumption.views.create_table_data',
        MagicMock(return_value=MOCK_TABLE_DATA))
    def test_summary__raise_consmption_http404(self):
        request = mock_summary_request()
        # execute
        with self.assertRaises(Http404):
            summary(request)

    # raise error on create_table_data
    @patch(
        'consumption.views.create_chart_data',
        MagicMock(return_value=MOCK_CHART_DATA))
    @patch(
        'consumption.views.create_table_data',
        MagicMock(side_effect=User.DoesNotExist))
    def test_summary__raise_user_http404(self):
        request = mock_summary_request()
        # execute
        with self.assertRaises(Http404):
            summary(request)


class DetailTestcase(TransactionTestCase):
    """Test for detail view
    """
    # mock create_chart_data and create_table_data
    @patch(
        'consumption.views.create_user_chart_data',
        MagicMock(return_value=MOCK_USER_CHART_DATA))
    def test_detail(self):
        test_fixtures.UserTestData.setUp(test_fixtures.USER_DATA_1)
        request = mock_detail_request(test_fixtures.USER_DATA_1['id'])
        expected_context = {
            'user_id': test_fixtures.USER_DATA_1['id'],
            'area': test_fixtures.USER_DATA_1['area'],
            'tariff': test_fixtures.USER_DATA_1['tariff'],
            'chart_data': {
                'labels': MOCK_USER_CHART_DATA['labels'],
                'total_data': MOCK_USER_CHART_DATA['data'],
            },
        }
        expected = render(
            request, 'consumption/detail.html', expected_context)

        # execute
        result = detail(request, test_fixtures.USER_DATA_1['id'])

        self.assertEqual(expected.status_code, result.status_code)

    # raise error on get user
    def test_detail__raise_consmption_http404(self):
        request = mock_detail_request(test_fixtures.USER_DATA_1['id'])
        # execute
        with self.assertRaises(Http404):
            detail(request, '111111')

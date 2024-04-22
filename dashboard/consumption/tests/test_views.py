from django.test import TestCase
from django.urls import reverse
from ..models import User, Consumption
from datetime import datetime


class SummaryTests(TestCase):
    # SummaryViewのテストクラス
    def setUp(self):
        user = User.objects.create(user_id=1, user_area='test_area', user_tariff='test_tariff')

    def test_get(self):
        # GETステータスチェック
        response = self.client.get(reverse('summary'))
        self.assertEqual(response.status_code, 200)

    def test_get_data(self):
        # GETデータチェック
        response = self.client.get(reverse('summary'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['user_list'], ['<User: User object (1)>'])
        self.assertEqual(type(response.context['chart_1']), type('String'))
        self.assertEqual(type(response.context['chart_2']), type('String'))


class DetailTests(TestCase):
    # Detailのテストクラス
    def test_get(self):
        # GETステータスチェック
        response = self.client.get(reverse('detail', args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_get_data(self):
        # GETデータチェック
        response = self.client.get(reverse('detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user_id'], 1)
        self.assertEqual(type(response.context['chart_1']), type('String'))
        self.assertEqual(type(response.context['chart_2']), type('String'))

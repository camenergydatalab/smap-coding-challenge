# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from ..forms import UserForm, ConsumptionForm
from ..models import Area, Consumption, Tariff, User


# Create your tests here.
class UserFormTests(TestCase):

    def setUp(self):
        self.area = Area.objects.create(name='a1')
        self.tariff = Tariff.objects.create(plan='t1')

    def test_valid(self):
        """入力チェックパス"""
        form = UserForm({
            'id': 3000,
            'area': self.area.id,
            'tariff': self.tariff.id,
        })

        self.assertTrue(form.is_valid())

    def test_invalid_empty(self):
        """未入力"""
        form = UserForm({})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['id'].as_text(), '* This field is required.')
        self.assertEqual(form.errors['area'].as_text(), '* This field is required.')
        self.assertEqual(form.errors['tariff'].as_text(), '* This field is required.')

    def test_invalid_choice(self):
        """選択式データの不整値"""
        form = UserForm({
            'id': 3003,
            'area': -1,
            'tariff': -1,
        })

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['area'].as_text(),
            '* Select a valid choice. That choice is not one of the available choices.'
        )
        self.assertEqual(
            form.errors['tariff'].as_text(),
            '* Select a valid choice. That choice is not one of the available choices.'
        )

    def test_invalid_unique_user(self):
        """指定したユーザIDが重複しているか"""
        User.objects.create(id=3001, area=self.area, tariff=self.tariff)

        form = UserForm({
            'id': 3001,
            'area': self.area.id,
            'tariff': self.tariff.id,
        })

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['id'].as_text(), '* User with this Id already exists.')


class ConsumptionFormTests(TestCase):

    def setUp(self):
        self.area = Area.objects.create(name='a1')
        self.tariff = Tariff.objects.create(plan='t1')
        self.user = User.objects.create(id=3001, area=self.area, tariff=self.tariff)
        self.aware_datetime = timezone.make_aware(datetime(2016, 7, 15, 0, 0, 0))

        Consumption.objects.create(
            user=self.user,
            datetime=self.aware_datetime,
            value=300.0
        )

    def test_valid(self):
        """入力チェックパス"""
        form = ConsumptionForm({
            'user': self.user.id,
            'datetime': '2016-7-15 01:00:00',
            'value': 99999999.99,
        })

        self.assertTrue(form.is_valid())

    def test_invalid_empty(self):
        """未入力"""
        form = ConsumptionForm({})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['user'].as_text(), '* This field is required.')
        self.assertEqual(form.errors['datetime'].as_text(), '* This field is required.')
        self.assertEqual(form.errors['value'].as_text(), '* This field is required.')

    def test_invalid_illegal_value(self):
        """想定外の値の入力"""
        form = ConsumptionForm({
            'user': 0,
            'datetime': '2016-2-30 00:00:00',
            'value': 100000000.00,
        })

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['user'].as_text(),
            '* Select a valid choice. That choice is not one of the available choices.'
        )
        self.assertEqual(form.errors['datetime'].as_text(), '* Enter a valid date/time.')
        self.assertEqual(
            form.errors['value'].as_text(),
            '* Ensure that there are no more than 8 digits before the decimal point.'
        )

    def test_invalid_unique_recode(self):
        """ユーザ・日時重複"""
        form = ConsumptionForm({
            'user': self.user.id,
            'datetime': self.aware_datetime,
            'value': 100,
        })

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['__all__'].as_text(),
            '* Consumption with this User and Datetime already exists.'
        )

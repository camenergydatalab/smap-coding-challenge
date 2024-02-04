# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from ..forms import UserForm
from ..models import Area, Tariff, User, Consumption


# Create your tests here.
class UserFormTests(TestCase):

    def setUp(self):
        self.area = Area.objects.create(name='a1')
        self.tariff = Tariff.objects.create(plan='t1')

    def test_valid(self):
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

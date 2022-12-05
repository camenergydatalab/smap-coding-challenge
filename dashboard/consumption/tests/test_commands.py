# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys

from django.test import TestCase
from django.core.management import call_command
from io import StringIO

from consumption.models import User, Consumption, CalculatedConsumption


# class ImportCommandTest(TestCase):
#     def test_import(self):
#         out = StringIO()
#         err = StringIO()
#         call_command('import', stdout=out, stderr=err)
#
#         self.assertEqual(User.objects.all().count(), 60)
#         self.assertEqual(Consumption.objects.all().count(), 489600)
#         self.assertEqual(CalculatedConsumption.objects.count(), 170)

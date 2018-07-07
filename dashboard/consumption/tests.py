# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from dateutil.parser import parse
from datetime import datetime

from .models import User, Consumption
from .factory import UserFactory, ConsumptionFactory

import calendar

class UserTests(TestCase):
    def test_is_empty(self):
        user_a1_1 = UserFactory(area='a1')
        self.assertEqual(user_a1_1.aggregated_consumptions().count(), 0)

    def test_aggregated_consumptions(self):
        user_a1_1 = UserFactory(area='a1')

        for i in range(7, 13):
            _, last_day = calendar.monthrange(2016, i)
            ConsumptionFactory(
                user_id=user_a1_1.id,
                datetime=parse('2016-{0:02d}-01 00:00:00+0000'.format(i))
            )
            ConsumptionFactory(
                user_id=user_a1_1.id, consumption=100,
                datetime=parse('2016-{0:02d}-{1} 23:30:00+0000'.format(i, last_day))
            )
        ConsumptionFactory(user_id=user_a1_1.id, datetime=parse('2017-01-01 00:00:00+0000'))
        ConsumptionFactory(user_id=user_a1_1.id, consumption=100, datetime=parse('2017-01-01 23:30:00+0000'))

        agg_consumptions = user_a1_1.aggregated_consumptions()

        # assert year, month
        for i in range(0, 6):
            self.assertEqual(agg_consumptions[i]['year'], 2016)
            self.assertEqual(agg_consumptions[i]['month'], i + 7)
        self.assertEqual(agg_consumptions[6]['year'], 2017)
        self.assertEqual(agg_consumptions[6]['month'], 1)

        # assert sum, max, average, count
        for i in range(0, 7):
            self.assertEqual(agg_consumptions[i]['sum'], 400)
            self.assertEqual(agg_consumptions[i]['max'], 300)
            self.assertEqual(agg_consumptions[i]['average'], 200)
            self.assertEqual(agg_consumptions[i]['count'], 2)


class ConsumptionTests(TestCase):
    def test_is_empty(self):
        agg_consumptions = Consumption.aggregated_consumptions_by_area()
        self.assertEqual(agg_consumptions.count(), 0)

    def test_sum_one_area_one_user_consumption_at_time_zone_japan(self):
        user_a1_1 = UserFactory(area='a1')

        for i in range(7, 13):
            ConsumptionFactory(
                user_id=user_a1_1.id,
                datetime=datetime.strptime("2016-{0:02d}-01+0900".format(i), '%Y-%m-%d%z')
            )
        ConsumptionFactory(user_id=user_a1_1.id, datetime=datetime.strptime('2017-01-01+0900', '%Y-%m-%d%z'))

        agg_consumptions = Consumption.aggregated_consumptions_by_area(timezone='Japan')
        a1_agg_consumptions = agg_consumptions.filter(user__area='a1')

        # assert year
        for i in range(0, 6):
            self.assertEqual(a1_agg_consumptions[i]['year'], 2016)
        self.assertEqual(a1_agg_consumptions[6]['year'], 2017)

        # assert month
        for i in range(0, 6):
            self.assertEqual(a1_agg_consumptions[i]['month'], i + 7)
        self.assertEqual(a1_agg_consumptions[6]['month'], 1)

        # assert user_count
        for i in range(0, 7):
            self.assertEqual(a1_agg_consumptions[i]['user_count'], 1)

        # assert agg_consumption(sum)
        for i in range(0, 7):
            self.assertEqual(a1_agg_consumptions[i]['agg_consumption'], 300)

    def test_avg_two_areas_four_users_at_time_zone_utc(self):
        user_a1_1 = UserFactory(area='a1')
        user_a1_2 = UserFactory(area='a1')
        user_a2_1 = UserFactory(area='a2')
        user_a2_2 = UserFactory(area='a2')

        for i in range(7, 13):
            ConsumptionFactory(
                user_id=user_a1_1.id,
                datetime=datetime.strptime("2016-{0:02d}-01+0000".format(i), '%Y-%m-%d%z')
            )
            ConsumptionFactory(
                user_id=user_a1_2.id, consumption=500,
                datetime=datetime.strptime("2016-{0:02d}-01+0000".format(i), '%Y-%m-%d%z')
            )
            ConsumptionFactory(
                user_id=user_a2_1.id,
                datetime=datetime.strptime("2016-{0:02d}-01+0000".format(i), '%Y-%m-%d%z')
            )
            ConsumptionFactory(
                user_id=user_a2_2.id, consumption=600,
                datetime=datetime.strptime("2016-{0:02d}-01+0000".format(i), '%Y-%m-%d%z')
            )
        ConsumptionFactory(user_id=user_a1_1.id, datetime=datetime.strptime('2017-01-01+0000', '%Y-%m-%d%z'))
        ConsumptionFactory(user_id=user_a1_2.id, consumption=500,
                           datetime=datetime.strptime('2017-01-01+0000', '%Y-%m-%d%z'))
        ConsumptionFactory(user_id=user_a2_1.id, datetime=datetime.strptime('2017-01-01+0000', '%Y-%m-%d%z'))
        ConsumptionFactory(user_id=user_a2_2.id, consumption=600,
                           datetime=datetime.strptime('2017-01-01+0000', '%Y-%m-%d%z'))

        agg_consumptions = Consumption.aggregated_consumptions_by_area(agg_type='avg')
        a1_agg_consumptions = agg_consumptions.filter(user__area='a1')
        a2_agg_consumptions = agg_consumptions.filter(user__area='a2')

        # assert year
        for i in range(0, 6):
            self.assertEqual(a1_agg_consumptions[i]['year'], 2016)
            self.assertEqual(a2_agg_consumptions[i]['year'], 2016)
        self.assertEqual(a1_agg_consumptions[6]['year'], 2017)
        self.assertEqual(a2_agg_consumptions[6]['year'], 2017)

        # assert month
        for i in range(0, 6):
            self.assertEqual(a1_agg_consumptions[i]['month'], i + 7)
            self.assertEqual(a2_agg_consumptions[i]['month'], i + 7)
        self.assertEqual(a1_agg_consumptions[6]['month'], 1)
        self.assertEqual(a2_agg_consumptions[6]['month'], 1)

        # assert user_count
        for i in range(0, 7):
            self.assertEqual(a1_agg_consumptions[i]['user_count'], 2)
            self.assertEqual(a2_agg_consumptions[i]['user_count'], 2)

        # assert agg_consumption(sum)
        for i in range(0, 7):
            self.assertEqual(a1_agg_consumptions[i]['agg_consumption'], 400)
            self.assertEqual(a2_agg_consumptions[i]['agg_consumption'], 450)


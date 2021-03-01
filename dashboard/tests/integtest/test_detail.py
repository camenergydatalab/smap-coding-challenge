# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import LiveServerTestCase
from django.urls import reverse_lazy
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from tests import test_fixtures


# consumption data group by user
USER_1_CONSUM_LIST = [
    test_fixtures.CONSUM_DATA_USER_1_1, test_fixtures.CONSUM_DATA_USER_1_2,
    test_fixtures.CONSUM_DATA_USER_1_3, test_fixtures.CONSUM_DATA_USER_1_4,
    test_fixtures.CONSUM_DATA_USER_1_5
]


class DetailTest(LiveServerTestCase):
    """Test for Detail view

    Test cases for Detail view.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # prepare data
        test_fixtures.UserTestData.setUp(test_fixtures.USER_DATA_1)
        for consum_data in USER_1_CONSUM_LIST:
            test_fixtures.ConsumptionTestData.setUp(consum_data)

        o = Options()
        # o.binary_location = SELENIUM_SETTING['binary_location'] # if needed
        o.add_argument(test_fixtures.SELENIUM_SETTING['headless'])
        o.add_argument(test_fixtures.SELENIUM_SETTING['disable-gpu'])
        o.add_argument(test_fixtures.SELENIUM_SETTING['no-sandbox'])
        o.add_argument(test_fixtures.SELENIUM_SETTING['window-size'])
        cls.selenium = WebDriver(
            executable_path=test_fixtures.SELENIUM_SETTING[
                'chromedriver_path'],
            options=o
        )

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_summary(self):
        self.selenium.get(
            '{}{}'.format(
                self.live_server_url,
                str(reverse_lazy(
                    'detail', kwargs={'user_id': test_fixtures.USER_1}))
            )
        )
        chart_classes = self.selenium.find_elements_by_class_name("chart")

        # number of elements are one
        self.assertEqual(len(chart_classes), 1)

        # total Chart Part

        # h2, span tags
        chart_title = chart_classes[0].find_element_by_tag_name('h2').text
        self.assertEqual(
            chart_title,
            '1. User id {} Consumption every 30 minutes'.format(
                test_fixtures.USER_1
            )
        )
        chart_spans = chart_classes[0].find_elements_by_tag_name('span')
        self.assertEqual(chart_spans[0].text, 'Time Period:')
        self.assertEqual(chart_spans[1].text, '~')

        # Time period select, btn tags

        # "Start From" options
        chart_start = self.selenium.find_element_by_id(
            "user-charts-start-from")
        chart_start_options = chart_start.find_elements_by_tag_name("option")
        # number of options are three because only showing time 00:00:00"
        self.assertEqual(len(chart_start_options), 3)
        # 1st option (selected)
        self.assertEqual(
            chart_start_options[0].get_attribute("selected"), 'true')
        self.assertEqual(chart_start_options[0].get_attribute("value"), '0')
        self.assertEqual(
            chart_start_options[0].get_attribute("label"),
            test_fixtures.TEST_DATETIME_1.strftime("%Y-%m-%d %H:%M:%S"))
        # 2nd option
        self.assertEqual(chart_start_options[1].get_attribute("value"), '3')
        self.assertEqual(
            chart_start_options[1].get_attribute("label"),
            test_fixtures.TEST_DATETIME_4.strftime("%Y-%m-%d %H:%M:%S"))
        # 3rd option
        self.assertEqual(chart_start_options[2].get_attribute("value"), '4')
        self.assertEqual(
            chart_start_options[2].get_attribute("label"),
            test_fixtures.TEST_DATETIME_5.strftime("%Y-%m-%d %H:%M:%S"))

        # "End To" options
        chart_end = self.selenium.find_element_by_id(
            "user-charts-end-to")
        chart_end_options = chart_end.find_elements_by_tag_name("option")
        self.assertEqual(len(chart_end_options), 3)
        # 1st option
        self.assertEqual(chart_end_options[0].get_attribute("value"), '0')
        self.assertEqual(
            chart_end_options[0].get_attribute("label"),
            test_fixtures.TEST_DATETIME_1.strftime("%Y-%m-%d %H:%M:%S"))
        # 2nd option
        self.assertEqual(chart_end_options[1].get_attribute("value"), '3')
        self.assertEqual(
            chart_end_options[1].get_attribute("label"),
            test_fixtures.TEST_DATETIME_4.strftime("%Y-%m-%d %H:%M:%S"))
        # 3rd option (selected)
        self.assertEqual(
            chart_end_options[0].get_attribute("selected"), 'true')
        self.assertEqual(chart_end_options[2].get_attribute("value"), '4')
        self.assertEqual(
            chart_end_options[2].get_attribute("label"),
            test_fixtures.TEST_DATETIME_5.strftime("%Y-%m-%d %H:%M:%S"))

        # "Apply" button
        # select 2nd one
        Select(chart_end).select_by_index(1)
        chart_apply = self.selenium.find_element_by_id("user-charts-filter")
        chart_apply.click()

        # select 2nd one
        Select(chart_end).select_by_index(1)
        chart_apply.click()
        # assert alert popup when end index is over start index
        Select(chart_start).select_by_index(1)
        Select(chart_end).select_by_index(0)
        chart_apply.click()
        wait = WebDriverWait(self.selenium, 10)
        wait.until(EC.alert_is_present())
        total_alert = self.selenium.switch_to.alert
        self.assertIn('Invalid time period', total_alert.text)
        total_alert.accept()

        # Table Part

        table_class = self.selenium.find_elements_by_class_name("user-info")[0]

        # h2 tags
        table_h2 = table_class.find_element_by_tag_name('h2')
        self.assertEqual(table_h2.text, '2. User Info')

        # th tags
        table_th_list = table_class.find_elements_by_tag_name('th')
        self.assertEqual(table_th_list[0].text, 'id')
        self.assertEqual(table_th_list[1].text, 'area')
        self.assertEqual(table_th_list[2].text, 'tariff')

        # td tags
        table_td_list = table_class.find_elements_by_tag_name('td')
        self.assertEqual(
            table_td_list[0].text, str(test_fixtures.USER_DATA_1['id']))
        self.assertEqual(
            table_td_list[1].text, str(test_fixtures.USER_DATA_1['area']))
        self.assertEqual(
            table_td_list[2].text, str(test_fixtures.USER_DATA_1['tariff']))

        # chek browser error not occured
        for log in self.selenium.get_log('browser'):
            self.assertNotIn('Error', log['message'])

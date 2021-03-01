# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import os
import time
from functools import reduce

from django.test import LiveServerTestCase
from django.urls import reverse_lazy
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from tests import test_fixtures

# user data
ALL_USER_DATA_LIST = [
    test_fixtures.USER_DATA_1, test_fixtures.USER_DATA_2,
    test_fixtures.USER_DATA_3
]

# consumption data group by user
USER_1_CONSUM_LIST = [
    test_fixtures.CONSUM_DATA_USER_1_1, test_fixtures.CONSUM_DATA_USER_1_2,
    test_fixtures.CONSUM_DATA_USER_1_3, test_fixtures.CONSUM_DATA_USER_1_4,
    test_fixtures.CONSUM_DATA_USER_1_5
]
USER_2_CONSUM_LIST = [
    test_fixtures.CONSUM_DATA_USER_2_1, test_fixtures.CONSUM_DATA_USER_2_2,
    test_fixtures.CONSUM_DATA_USER_2_3, test_fixtures.CONSUM_DATA_USER_2_4,
    test_fixtures.CONSUM_DATA_USER_2_5
]
USER_3_CONSUM_LIST = [
    test_fixtures.CONSUM_DATA_USER_3_1, test_fixtures.CONSUM_DATA_USER_3_2,
    test_fixtures.CONSUM_DATA_USER_3_3, test_fixtures.CONSUM_DATA_USER_3_4,
    test_fixtures.CONSUM_DATA_USER_3_5
]
# flatten list of each user's consumption data
ALL_CONSUM_DATA_LIST = reduce(
    lambda a, b: a + b,
    [USER_1_CONSUM_LIST, USER_2_CONSUM_LIST, USER_3_CONSUM_LIST]
)


MOCK_DOWNLOAD_CSV_RESULT = [
    [
        'ID', 'Area', 'Tariff',
        'Average Consumption (kWh)',
        "Percentage of consumption to top user's average consumption"
    ],
    ['1111', 'a2', 't2', '480', '72.72727272727273'],
    ['1234', 'a1', 't1', '300', '45.45454545454545'],
    ['3333', 'a3', 't3', '660', '100']
]

DOWNLOAD_CSV_PARH = os.path.join(test_fixtures.BASE_DIR, 'data.csv')


def delete_downloaded_csv():
    """delete csv which is downloaded by browser manipulation
    """
    try:
        os.remove(DOWNLOAD_CSV_PARH)
    except FileNotFoundError:
        pass


def wait_download_seconds(file_path, wait_seconds):
    """delete csv which is downloaded by browser manipulation

    Args:
        file_path (str): file path
        wait_seconds (int): seconds for waiting

    Raises:
        FileNotFoundError: if file not downloaded in specified seconds
    """
    seconds = 0
    while not os.path.exists(file_path):
        time.sleep(1)
        seconds += 1
        if seconds > wait_seconds:
            raise FileNotFoundError


class SummaryTest(LiveServerTestCase):
    """Test for Summary view

    Test cases for Summary view.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        delete_downloaded_csv()
        # prepare data
        for user_data in ALL_USER_DATA_LIST:
            test_fixtures.UserTestData.setUp(user_data)
        for consum_data in ALL_CONSUM_DATA_LIST:
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
        delete_downloaded_csv()
        cls.selenium.quit()
        super().tearDownClass()

    def test_summary(self):
        self.selenium.get(
            '{}{}'.format(
                self.live_server_url,
                str(reverse_lazy('summary'))
            )
        )
        chart_classes = self.selenium.find_elements_by_class_name("chart")

        # number of elements are two
        self.assertEqual(len(chart_classes), 2)

        # total Chart Part

        # h2, span tags
        total_h2 = chart_classes[0].find_element_by_tag_name('h2').text
        self.assertEqual(total_h2, '1-1. Total Consumption every 30 minutes')
        total_spans = chart_classes[0].find_elements_by_tag_name('span')
        self.assertEqual(total_spans[0].text, 'Time Period:')
        self.assertEqual(total_spans[1].text, '~')

        # Time period select, btn tags

        # "Start From" options
        total_start = self.selenium.find_element_by_id(
            "total-charts-start-from")
        total_start_options = total_start.find_elements_by_tag_name("option")
        # number of options are three because only showing time 00:00:00"
        self.assertEqual(len(total_start_options), 3)
        # 1st option (selected)
        self.assertEqual(
            total_start_options[0].get_attribute("selected"), 'true')
        self.assertEqual(total_start_options[0].get_attribute("value"), '0')
        self.assertEqual(
            total_start_options[0].get_attribute("label"),
            test_fixtures.TEST_DATETIME_1.strftime("%Y-%m-%d %H:%M:%S"))
        # 2nd option
        self.assertEqual(total_start_options[1].get_attribute("value"), '3')
        self.assertEqual(
            total_start_options[1].get_attribute("label"),
            test_fixtures.TEST_DATETIME_4.strftime("%Y-%m-%d %H:%M:%S"))
        # 3rd option
        self.assertEqual(total_start_options[2].get_attribute("value"), '4')
        self.assertEqual(
            total_start_options[2].get_attribute("label"),
            test_fixtures.TEST_DATETIME_5.strftime("%Y-%m-%d %H:%M:%S"))

        # "End To" options
        total_end = self.selenium.find_element_by_id(
            "total-charts-end-to")
        total_end_options = total_end.find_elements_by_tag_name("option")
        self.assertEqual(len(total_end_options), 3)
        # 1st option
        self.assertEqual(total_end_options[0].get_attribute("value"), '0')
        self.assertEqual(
            total_end_options[0].get_attribute("label"),
            test_fixtures.TEST_DATETIME_1.strftime("%Y-%m-%d %H:%M:%S"))
        # 2nd option
        self.assertEqual(total_end_options[1].get_attribute("value"), '3')
        self.assertEqual(
            total_end_options[1].get_attribute("label"),
            test_fixtures.TEST_DATETIME_4.strftime("%Y-%m-%d %H:%M:%S"))
        # 3rd option (selected)
        self.assertEqual(
            total_end_options[0].get_attribute("selected"), 'true')
        self.assertEqual(total_end_options[2].get_attribute("value"), '4')
        self.assertEqual(
            total_end_options[2].get_attribute("label"),
            test_fixtures.TEST_DATETIME_5.strftime("%Y-%m-%d %H:%M:%S"))

        # "Apply" button
        # select 2nd one
        Select(total_end).select_by_index(1)
        total_apply = self.selenium.find_element_by_id("total-charts-filter")
        total_apply.click()

        # select 2nd one
        Select(total_end).select_by_index(1)
        total_apply.click()
        # assert alert popup when end index is over start index
        Select(total_start).select_by_index(1)
        Select(total_end).select_by_index(0)
        # import pdb;pdb.set_trace()
        total_apply.click()
        wait = WebDriverWait(self.selenium, 10)
        wait.until(EC.alert_is_present())
        # import pdb;pdb.set_trace()
        total_alert = self.selenium.switch_to.alert
        self.assertIn('Invalid time period', total_alert.text)
        total_alert.accept()

        # Average Chart Part

        # h2, span tags
        avg_h2 = chart_classes[1].find_element_by_tag_name('h2').text
        self.assertEqual(avg_h2, '1-2. Average Consumption every 30 minutes')
        avg_spans = chart_classes[1].find_elements_by_tag_name('span')
        self.assertEqual(avg_spans[0].text, 'Time Period:')
        self.assertEqual(avg_spans[1].text, '~')

        # Time period select, btn tags

        # "Start From" options
        avg_start = self.selenium.find_element_by_id(
            "avg-charts-start-from")
        avg_start_options = avg_start.find_elements_by_tag_name("option")
        # number of options are three because only showing time 00:00:00"
        self.assertEqual(len(avg_start_options), 3)
        # 1st option (selected)
        self.assertEqual(
            avg_start_options[0].get_attribute("selected"), 'true')
        self.assertEqual(avg_start_options[0].get_attribute("value"), '0')
        self.assertEqual(
            avg_start_options[0].get_attribute("label"),
            test_fixtures.TEST_DATETIME_1.strftime("%Y-%m-%d %H:%M:%S"))
        # 2nd option
        self.assertEqual(avg_start_options[1].get_attribute("value"), '3')
        self.assertEqual(
            avg_start_options[1].get_attribute("label"),
            test_fixtures.TEST_DATETIME_4.strftime("%Y-%m-%d %H:%M:%S"))
        # 3rd option
        self.assertEqual(avg_start_options[2].get_attribute("value"), '4')
        self.assertEqual(
            avg_start_options[2].get_attribute("label"),
            test_fixtures.TEST_DATETIME_5.strftime("%Y-%m-%d %H:%M:%S"))

        # "End To" options
        avg_end = self.selenium.find_element_by_id(
            "avg-charts-end-to")
        avg_end_options = avg_end.find_elements_by_tag_name("option")
        self.assertEqual(len(avg_end_options), 3)
        # 1st option
        self.assertEqual(avg_end_options[0].get_attribute("value"), '0')
        self.assertEqual(
            avg_end_options[0].get_attribute("label"),
            test_fixtures.TEST_DATETIME_1.strftime("%Y-%m-%d %H:%M:%S"))
        # 2nd option
        self.assertEqual(avg_end_options[1].get_attribute("value"), '3')
        self.assertEqual(
            avg_end_options[1].get_attribute("label"),
            test_fixtures.TEST_DATETIME_4.strftime("%Y-%m-%d %H:%M:%S"))
        # 3rd option (selected)
        self.assertEqual(
            avg_end_options[0].get_attribute("selected"), 'true')
        self.assertEqual(avg_end_options[2].get_attribute("value"), '4')
        self.assertEqual(
            avg_end_options[2].get_attribute("label"),
            test_fixtures.TEST_DATETIME_5.strftime("%Y-%m-%d %H:%M:%S"))

        # "Apply" button
        # select 2nd one
        Select(avg_end).select_by_index(1)
        avg_apply = self.selenium.find_element_by_id("avg-charts-filter")
        avg_apply.click()

        # select 2nd one
        avg_apply = self.selenium.find_element_by_id("avg-charts-filter")
        Select(avg_end).select_by_index(1)
        avg_apply.click()
        # assert alert popup when end index is over start index
        Select(avg_start).select_by_index(1)
        Select(avg_end).select_by_index(0)
        avg_apply.click()
        wait = WebDriverWait(self.selenium, 10)
        wait.until(EC.alert_is_present())
        avg_alert = self.selenium.switch_to.alert
        self.assertIn('Invalid time period', avg_alert.text)
        avg_alert.accept()

        # Table Part

        table_class = self.selenium.find_element_by_class_name("table")

        # h1, h2 tags
        table_h1 = table_class.find_element_by_tag_name('h1').text
        self.assertEqual(
            table_h1, '2. All Users and Its Average Consumption in All Periods')
        table_h3 = table_class.find_element_by_tag_name('h3').text
        self.assertEqual(
            table_h3, "To see user's detail info, please click the row.")

        # csv download button
        table_btn = self.selenium.find_element_by_id("download-csv")
        self.assertEqual(
            table_btn.text, "Download CSV")
        # check downloaded csv file
        table_btn.click()
        wait_download_seconds(DOWNLOAD_CSV_PARH, 10)
        with open(DOWNLOAD_CSV_PARH) as file:
            reader = csv.reader(file)
            data = list(reader)
            # only one record
            self.assertEqual(len(data), 4)
            self.assertCountEqual(data[0], MOCK_DOWNLOAD_CSV_RESULT[0])
            self.assertCountEqual(data[1], MOCK_DOWNLOAD_CSV_RESULT[1])
            self.assertCountEqual(data[2], MOCK_DOWNLOAD_CSV_RESULT[2])
            self.assertCountEqual(data[3], MOCK_DOWNLOAD_CSV_RESULT[3])

        # chek browser error not occured
        for log in self.selenium.get_log('browser'):
            self.assertNotIn('Error', log['message'])

        # check if opening detail view is working
        cell = table_class.find_element_by_class_name(
            'tabulator-cell')
        user_id_in_cell = cell.text
        cell.click()
        # switch tab and check url
        self.selenium.switch_to.window(self.selenium.window_handles[1])
        expexred_detail_url = '{}{}'.format(
            self.live_server_url,
            str(reverse_lazy('detail', kwargs={'user_id': user_id_in_cell}))
        )

        self.assertEqual(self.selenium.current_url, expexred_detail_url)

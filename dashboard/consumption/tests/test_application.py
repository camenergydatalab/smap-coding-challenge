# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import pandas as pd
from django.test import TestCase

from ..application.consumption_csv_data_processor import \
    ConsumptionCSVDataProcessor
from ..config import TEST_CONSUMPTION_DIR, TEST_PREPROCESSED_CONSUMPTION_DIR


class ConsumptionCSVDataProcessorTest(TestCase):
    def test_exec(self):
        processor = ConsumptionCSVDataProcessor(
            TEST_CONSUMPTION_DIR, TEST_PREPROCESSED_CONSUMPTION_DIR
        )

        processor.exec()

        # 検証コード
        test_preprocessor_consumption_file = os.path.join(
            TEST_PREPROCESSED_CONSUMPTION_DIR, "3000.csv"
        )
        df = pd.read_csv(test_preprocessor_consumption_file)

        # 1日のレコード数が、48件
        self.assertEqual(len(list(df["datetime"])), 48)

        # 2016-07-15 01:30:00 を保管していることを確認
        df = df.set_index("datetime")
        self.assertEqual(df.loc["2016-07-15 01:30:00"]["consumption"], 10.0)

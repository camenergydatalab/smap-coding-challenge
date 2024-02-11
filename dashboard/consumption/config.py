# -*- coding: utf-8 -*-

import os

SMAP_BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

USER_DATA_FILE = os.path.join(SMAP_BASE_DIR, "data", "user_data.csv")
CONSUMPTION_DIR = os.path.join(SMAP_BASE_DIR, "data", "consumption")
PREPROCESSED_CONSUMPTION_DIR = os.path.join(
    SMAP_BASE_DIR, "preprocessed_data", "consumption"
)

TEST_CONSUMPTION_DIR = os.path.join(SMAP_BASE_DIR, "test_data", "consumption")
TEST_PREPROCESSED_CONSUMPTION_DIR = os.path.join(
    SMAP_BASE_DIR, "test_preprocessed_data", "consumption"
)

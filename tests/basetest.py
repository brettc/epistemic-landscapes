import sys
import os
import pytest

# Magically append the root folder so we can run stuff directly from the tests
# folder if we want
TEST_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH, here = os.path.split(TEST_PATH)
sys.path.append(ROOT_PATH)

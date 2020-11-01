import unittest
from datetime import datetime

from logic import Helpers


class HelpersTest(unittest.TestCase):
    def test_join_url_parts(self):
        self.assertEqual('https://myWebsite/eimer/0815', Helpers.join_url_parts('https://myWebsite', 'eimer', '0815'))

    def test_round_to_decimals_one(self):
        self.assertEqual('0.4', Helpers.round_to_decimals(0.428, 1))

    def test_round_to_decimals_zero(self):
        self.assertEqual('0', Helpers.round_to_decimals(0.428, 0))

    def test_is_dayTime_true(self):
        sunrise = datetime(year=2020, month=11, day=1, hour=8, minute=0, second=0).timestamp()
        sunset = datetime(year=2020, month=11, day=1, hour=17, minute=0, second=0).timestamp()

        currentTimestamp = datetime(year=2020, month=11, day=1, hour=12, minute=0, second=0).timestamp()

        self.assertTrue(Helpers.is_dayTime(sunrise, sunset, currentTimestamp))

    def test_is_dayTime_false_before(self):
        sunrise = datetime(year=2020, month=11, day=1, hour=8, minute=0, second=0).timestamp()
        sunset = datetime(year=2020, month=11, day=1, hour=17, minute=0, second=0).timestamp()

        currentTimestamp = datetime(year=2020, month=11, day=1, hour=4, minute=0, second=0).timestamp()

        self.assertFalse(Helpers.is_dayTime(sunrise, sunset, currentTimestamp))

    def test_is_dayTime_false_after(self):
        sunrise = datetime(year=2020, month=11, day=1, hour=8, minute=0, second=0).timestamp()
        sunset = datetime(year=2020, month=11, day=1, hour=17, minute=0, second=0).timestamp()

        currentTimestamp = datetime(year=2020, month=11, day=1, hour=18, minute=0, second=0).timestamp()

        self.assertFalse(Helpers.is_dayTime(sunrise, sunset, currentTimestamp))

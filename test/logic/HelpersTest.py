import unittest
from datetime import datetime

import pytz

from logic import Helpers


class HelpersTest(unittest.TestCase):
    def test_join_url_parts(self):
        self.assertEqual('https://myWebsite/eimer/0815', Helpers.join_url_parts('https://myWebsite', 'eimer', '0815'))

    def test_round_to_decimals_one(self):
        self.assertEqual('0.4', Helpers.round_to_decimals(0.428, 1))

    def test_round_to_decimals_zero(self):
        self.assertEqual('0', Helpers.round_to_decimals(0.428, 0))

    def test_is_dayTime_true(self):
        sunrise = datetime(year=2020, month=11, day=1, hour=8, minute=0, second=0)
        sunset = datetime(year=2020, month=11, day=1, hour=17, minute=0, second=0)

        currentTimestamp = datetime(year=2020, month=11, day=1, hour=12, minute=0, second=0)

        self.assertTrue(Helpers.is_dayTime(sunrise, sunset, currentTimestamp))

    def test_is_dayTime_false_before(self):
        sunrise = datetime(year=2020, month=11, day=1, hour=8, minute=0, second=0)
        sunset = datetime(year=2020, month=11, day=1, hour=17, minute=0, second=0)

        currentTimestamp = datetime(year=2020, month=11, day=1, hour=4, minute=0, second=0)

        self.assertFalse(Helpers.is_dayTime(sunrise, sunset, currentTimestamp))

    def test_is_dayTime_false_after(self):
        sunrise = datetime(year=2020, month=11, day=1, hour=8, minute=0, second=0)
        sunset = datetime(year=2020, month=11, day=1, hour=17, minute=0, second=0)

        currentTimestamp = datetime(year=2020, month=11, day=1, hour=18, minute=0, second=0)

        self.assertFalse(Helpers.is_dayTime(sunrise, sunset, currentTimestamp))

    def test_is_dayTime_true_complex(self):
        timeZone = pytz.timezone('Europe/Berlin')
        sunrise = Helpers.timestamp_to_timezone(1604296782, timeZone)
        sunset = Helpers.timestamp_to_timezone(1604331478, timeZone)

        now = timeZone.localize(datetime(year=2020, month=11, day=2, hour=15, minute=0, second=0))

        self.assertTrue(Helpers.is_dayTime(sunrise, sunset, now))

    def test_timestamp_to_timezone_berlin(self):
        timestamp = 1604331478
        timeZone = pytz.timezone('Europe/Berlin')

        expected = datetime(year=2020, month=11, day=2, hour=16, minute=37, second=58)
        self.__compareDates(expected, Helpers.timestamp_to_timezone(timestamp, timeZone))

    def test_timestamp_to_timezone_london(self):
        timestamp = 1604331478
        timeZone = pytz.timezone('Europe/London')
        expected = datetime(year=2020, month=11, day=2, hour=15, minute=37, second=58, tzinfo=timeZone)
        self.__compareDates(expected, Helpers.timestamp_to_timezone(timestamp, timeZone))

    def __compareDates(self, a: datetime, b: datetime):
        self.assertEqual(a.year, b.year)
        self.assertEqual(a.month, b.month)
        self.assertEqual(a.day, b.day)
        self.assertEqual(a.hour, b.hour)
        self.assertEqual(a.minute, b.minute)
        self.assertEqual(a.second, b.second)
        self.assertEqual(a.microsecond, b.microsecond)

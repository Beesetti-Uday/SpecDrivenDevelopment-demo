import unittest
import datetime
from db import needs_rollover, parse_date

class TestDatabaseRollover(unittest.TestCase):
    def test_parse_date(self):
        self.assertEqual(parse_date("2026-05-25"), datetime.date(2026, 5, 25))
        self.assertIsNone(parse_date("invalid-date"))
        self.assertIsNone(parse_date(""))

    def test_daily_rollover(self):
        # Completed today, should not rollover today
        self.assertFalse(needs_rollover('daily', '2026-05-25', datetime.date(2026, 5, 25)))
        # Completed yesterday, should rollover today
        self.assertTrue(needs_rollover('daily', '2026-05-24', datetime.date(2026, 5, 25)))

    def test_weekly_rollover(self):
        # 2026-05-25 is Monday of week 22.
        # 2026-05-24 is Sunday of week 21.
        # Completed same week, should not rollover
        self.assertFalse(needs_rollover('weekly', '2026-05-26', datetime.date(2026, 5, 28)))
        # Completed previous week, should rollover
        self.assertTrue(needs_rollover('weekly', '2026-05-24', datetime.date(2026, 5, 25)))

    def test_monthly_rollover(self):
        # Completed same month, should not rollover
        self.assertFalse(needs_rollover('monthly', '2026-05-01', datetime.date(2026, 5, 25)))
        # Completed previous month, should rollover
        self.assertTrue(needs_rollover('monthly', '2026-04-30', datetime.date(2026, 5, 1)))

if __name__ == '__main__':
    unittest.main()

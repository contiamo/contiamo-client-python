import unittest
import json
import datetime

from . import utils
from contiamo.utils import parse_query_result as parse_json


class ParseJsonTestCase(unittest.TestCase):

    def test_simple(self):
        with open(utils.file_test_data('data_simple.json')) as data_file:
            result = json.load(data_file)
        df = parse_json(result)
        self.assertAlmostEqual(df['New Users'].iloc[0], 7447.0, 6)

    def test_hourly(self):
        with open(utils.file_test_data('data_hourly.json')) as data_file:
            result = json.load(data_file)
        df = parse_json(result)
        self.assertEqual(df['Date'].iloc[-1], datetime.datetime(2015, 12, 9, 23))

    def test_weekly(self):
        with open(utils.file_test_data('data_weekly.json')) as data_file:
            result = json.load(data_file)
        df = parse_json(result)
        self.assertEqual(df['Date'].iloc[0], datetime.datetime(2015, 11, 23))

    def test_no_parse(self):
        with open(utils.file_test_data('data_weekly.json')) as data_file:
            result = json.load(data_file)
        df = parse_json(result, parse_dates=False)
        self.assertEqual(df['Date'].iloc[0], '2015W48')

    def test_dimension(self):
        with open(utils.file_test_data('data_dimension.json')) as data_file:
            result = json.load(data_file)
        df = parse_json(result)
        self.assertEqual(df['Default Channel Grouping'].iloc[0], 'Direct')

    def test_date_dimension(self):
        with open(utils.file_test_data('data_date_dimension.json')) as data_file:
            result = json.load(data_file)
        df = parse_json(result)
        self.assertEqual(df['First purchase quarter'].iloc[0], datetime.datetime(2013, 7, 1))

    def test_nodate(self):
        with open(utils.file_test_data('data_nodate.json')) as data_file:
            result = json.load(data_file)
        df = parse_json(result)
        self.assertAlmostEqual(df['No. of orders'].iloc[0], 237.0, 6)

    def test_stat(self):
        with open(utils.file_test_data('data_stat.json')) as data_file:
            result = json.load(data_file)
        df = parse_json(result)
        self.assertAlmostEqual(df['Pageviews (Exponential Moving Average)'].iloc[0], 17562.0, 6)

    def test_calc(self):
        with open(utils.file_test_data('data_calc.json')) as data_file:
            result = json.load(data_file)
        df = parse_json(result)
        self.assertAlmostEqual(df['Calculation'].iloc[0], 1156540.0, 6)

    def test_comparison_period(self):
        with open(utils.file_test_data('data_comparison_period.json')) as data_file:
            result = json.load(data_file)
        df = parse_json(result)
        self.assertAlmostEqual(df['Pageviews (previous period)'].iloc[0], 19302.0, 6)

    def test_empty(self):
        with open(utils.file_test_data('data_empty.json')) as data_file:
            result = json.load(data_file)
        df = parse_json(result)
        self.assertEqual(len(df), 0)

    def test_duplicate_columns(self):
        with open(utils.file_test_data('data_duplicate_columns.json')) as data_file:
            result = json.load(data_file)
        df = parse_json(result)
        self.assertEqual(len(df.columns), 4)
        self.assertTrue(df.columns.is_unique)

    def test_duplicate_calculation(self):
        with open(utils.file_test_data('data_duplicate_calculation.json')) as data_file:
            result = json.load(data_file)
        df = parse_json(result)
        self.assertEqual(len(df.columns), 4)
        self.assertTrue(not df.columns.is_unique)


if __name__ == '__main__':
    unittest.main()

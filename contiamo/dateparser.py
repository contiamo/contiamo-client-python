import re
import pandas as pd
from isoweek import Week


class DateParser:
    """Inspects a date string to find out its date format and provides the right date parser"""

    def parse_second(date_string):
        return pd.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')

    def format_second(date):
        return date.strftime('%Y-%m-%dT%H:%M:%S')

    def parse_minute(date_string):
        return pd.datetime.strptime(date_string, '%Y-%m-%dT%H:%M')

    def format_minute(date):
        return date.strftime('%Y-%m-%dT%H:%M')

    def parse_hour(date_string):
        return pd.datetime.strptime(date_string, '%Y-%m-%dT%H')

    def format_hour(date):
        return date.strftime('%Y-%m-%dT%H')

    def parse_day(date_string):
        return pd.datetime.strptime(date_string, '%Y-%m-%d')

    def format_day(date):
        return date.strftime('%Y-%m-%d')

    def parse_week(date_string):
        split = date_string.split('W')
        date = Week(int(split[0]), int(split[1])).monday()
        return pd.datetime(date.year, date.month, date.day)

    def format_week(date):
        return Week.withdate(date).isoformat()

    def parse_month(date_string):
        return pd.datetime.strptime(date_string, '%Y-%m')

    def format_month(date):
        return date.strftime('%Y-%m')

    def parse_quarter(date_string):
        split = date_string.split('Q')
        return pd.datetime(int(split[0]), 1 + ((int(split[1])) - 1) * 3, 1)

    def format_quarter(date):
        return date.strftime('%Y') + 'Q' + str(((date.month - 1) // 3) + 1)

    def parse_year(date_string):
        return pd.datetime.strptime(date_string, '%Y')

    def format_year(date):
        return date.strftime('%Y')

    PERIOD_UNITS = [
        {
            'key': 'second',
            'regex': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$',
            'parser': parse_second,
            'formatter': format_second

        },
        {
            'key': 'minute',
            'regex': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$',
            'parser': parse_minute,
            'formatter': format_minute
        },
        {
            'key': 'hour',
            'regex': r'^\d{4}-\d{2}-\d{2}T\d{2}$',
            'parser': parse_hour,
            'formatter': format_hour
        },
        {
            'key': 'day',
            'regex': r'^\d{4}-\d{2}-\d{2}$',
            'parser': parse_day,
            'formatter': format_day
        },
        {
            'key': 'week',
            'regex': r'^\d{4}W\d{1,2}$',
            'parser': parse_week,
            'formatter': format_week
        },
        {
            'key': 'month',
            'regex': r'^\d{4}-\d{2}$',
            'parser': parse_month,
            'formatter': format_month
        },
        {
            'key': 'quarter',
            'regex': r'^\d{4}Q\d{1,2}$',
            'parser': parse_quarter,
            'formatter': format_quarter
        },
        {
            'key': 'year',
            'regex': r'^\d{4}$',
            'parser': parse_year,
            'formatter': format_year
        }
    ]

    def __init__(self):
        self.period_unit = None
        self.parser = None

    def identifyPeriodUnit(self, sample):
        for period_unit in self.PERIOD_UNITS:
            if re.search(period_unit['regex'], sample):
                self.period_unit = period_unit['key']
                self.parser = period_unit['parser']
                self.formatter = period_unit['formatter']
                break
        return self.period_unit

    def parse(self, date_string):
        return self.parser(date_string)

    def format(self, date):
        return self.formatter(date)

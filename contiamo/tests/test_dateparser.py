import unittest

from contiamo.dateparser import DateParser


class DateParseTestCase(unittest.TestCase):

    formats = [
        ['2014-12-31T23:59:59', 'second',  '2014-12-31T23:59:59'],
        ['2014-12-31T23:59',    'minute',  '2014-12-31T23:59:00'],
        ['2014-12-31T23',       'hour',    '2014-12-31T23:00:00'],
        ['2014-12-31',          'day',     '2014-12-31T00:00:00'],
        ['2014W01',             'week',    '2013-12-30T00:00:00'],
        ['2014W12',             'week',    '2014-03-17T00:00:00'],
        ['2014-12',             'month',   '2014-12-01T00:00:00'],
        ['2014Q1',              'quarter', '2014-01-01T00:00:00'],
        ['2014Q3',              'quarter', '2014-07-01T00:00:00'],
        ['2014',                'year',    '2014-01-01T00:00:00']
    ]

    def test_identification(self):
        for format in self.formats:
            parser = DateParser()
            self.assertEqual(parser.identifyPeriodUnit(format[0]), format[1])

    def test_parsing(self):
        for format in self.formats:
            parser = DateParser()
            parser.identifyPeriodUnit(format[0])
            date = parser.parse(format[0])
            self.assertEqual(date.strftime('%Y-%m-%dT%H:%M:%S'),
                             format[2], '{0} parsing failed'.format(format[1]))

    def test_formatting(self):
        for format in self.formats:
            parser = DateParser()
            parser.identifyPeriodUnit(format[0])
            date = parser.parse(format[0])
            self.assertEqual(parser.format(
                date), format[0], '{0} formatting failed'.format(format[1]))


if __name__ == '__main__':
    unittest.main()

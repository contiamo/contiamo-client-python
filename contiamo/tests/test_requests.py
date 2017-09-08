import unittest
import vcr
import os

try:
  import pandas
  import numpy as np
except ImportError:
  pandas = None

from contiamo.data import DataClient, select_date_columns, select_int_columns, preformat
from contiamo.public import query
from contiamo.errors import InvalidRequestError

import yaml
import warnings

try:
  config = yaml.safe_load(open('tests/data/test_config.yml'))
  api_base = config['api_base']
  contract_id = config['contract_id']
  contract_token = config['contract_token']
  query_id = config['query_id']
except FileNotFoundError:
  warnings.warn('These tests will be skipped, as they require configuration information that is unavailable.')
  config = None

data_client = DataClient(contract_id, contract_token, api_base=api_base)


@unittest.skipIf(not config, 'Configuration information is not available.')
class RequestsTestCase(unittest.TestCase):

  @unittest.skipIf(not pandas, 'The pandas package is not available.')
  def test_select_dates(self):
    df = pandas.DataFrame({'date': pandas.date_range('2016-01-01', periods=2)})
    df['datetime'] = pandas.to_datetime(df['date'].astype(str) + 'T01:00')
    df.loc[3] = None  # test NaT datetime
    self.assertEqual(select_date_columns(df), ['date'])
    df = pandas.DataFrame({'int': [0, 1], 'float': [0.1, 0.2], 'str': ['a', 'b']})
    self.assertEqual(select_date_columns(df), [])

  @unittest.skipIf(not pandas, 'The pandas package is not available.')
  def test_select_integers(self):
    df = pandas.DataFrame({
        'int': list(range(4)),
        'int2': [3, np.nan, 58, np.nan],
        'int3': [2, 57, np.nan, np.nan],
        'float': [2.5, 2.6, 2.7, 2.0],
    })
    self.assertEqual(set(select_int_columns(df)), set(['int2', 'int3']))

  @unittest.skipIf(not pandas, 'The pandas package is not available.')
  def test_preformat(self):
    df = pandas.DataFrame({
        'int': [3, np.nan, 58],
        'date': pandas.date_range('2016-01-01', periods=3),
    })
    preformat(df)
    expected = pandas.DataFrame({
      'int': ['3', np.nan, '58'],
      'date': ['2016-01-01', '2016-01-02', '2016-01-03'],
      })
    self.assertTrue(df.equals(expected))

  @vcr.use_cassette('tests/cassettes/test_purge.yaml')
  def test_purge(self):
    response = data_client.purge()
    self.assertTrue('status' in response)
    self.assertEqual(response['status'], 'ok')

  @vcr.use_cassette('tests/cassettes/test_discover.yaml')
  def test_discover(self):
    # need to purge data before discovering
    if not os.path.isfile('tests/cassettes/test_discover.yaml'):
      data_client.purge()
    response = data_client.discover(filename='tests/data/mock_data.csv')
    self.assertTrue('status' in response)
    self.assertEqual(response['status'], 'ok')

  @vcr.use_cassette('tests/cassettes/test_upload.yaml')
  def test_upload(self):
    response = data_client.upload(filename='tests/data/mock_data.csv')
    self.assertTrue('status' in response)
    self.assertEqual(response['status'], 'ok')

  @unittest.skipIf(not pandas, 'The pandas package is not available.')
  @vcr.use_cassette('tests/cassettes/test_upload.yaml')
  def test_upload_dataframe(self):
    df = pandas.DataFrame({'a': [1,3], 'b': [2,4]})
    response = data_client.upload(dataframe=df)
    self.assertTrue('status' in response)
    self.assertEqual(response['status'], 'ok')

  @vcr.use_cassette('tests/cassettes/test_query.yaml')
  def test_query(self):
    response = query(query_id, api_base=api_base)
    if pandas:
      self.assertTrue(isinstance(response, pandas.DataFrame))
    else:
      self.assertTrue(isinstance(response, dict))


@unittest.skipIf(not config, 'Configuration information is not available.')
class ErrorsTestCase(unittest.TestCase):

  def test_dataframe(self):
    df = {'a': [1,2,3], 'b': [4,5,6]}
    with self.assertRaises(InvalidRequestError):
      data_client.upload(dataframe=df)

  def test_no_argument(self):
    with self.assertRaises(InvalidRequestError):
      data_client.upload()

  @unittest.skipIf(not pandas, 'The pandas package is not available.')
  def test_two_arguments(self):
    df = pandas.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
    with self.assertRaises(InvalidRequestError):
      data_client.upload(dataframe=df, filename='tests/data/mock_data.csv')


if __name__ == '__main__':
  unittest.main()

import unittest
import vcr
import os

try:
  import pandas
except ImportError:
  pandas = None

from contiamo.data import DataClient
from contiamo.public import query

import yaml
import warnings

try:
  config = yaml.safe_load(open('tests/data/test_config.yml'))
  api_base = config['api_base']
  contract_id = config['contract_id']
  contract_token = config['contract_token']
  query_id = config['query_id']
except FileNotFoundError:
  warnings.warn("These tests will be skipped, as they require configuration information that is unavailable.")
  config = None

data_client = DataClient(contract_id, contract_token, api_base=api_base)


@unittest.skipIf(not config, "Configuration information is not available.")
class RequestsTestCase(unittest.TestCase):

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


if __name__ == '__main__':
  unittest.main()

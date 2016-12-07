import unittest

from contiamo.utils import query_url_from_identifier, contract_url_template_from_identifier


class IdentifierToUrl(unittest.TestCase):
  api_base = 'https://api.some-name.com'

  # Query URLs
  def test_query_url(self):
    url = query_url_from_identifier('query:olap:48590200:21237:eBMDTcG31VZzMTGFdnGBVnyyCyRFJLsDF12y8q8h2uQ', api_base=self.api_base)
    self.assertEqual(url, self.api_base + '/48590200/stored_query/21237.json?resource_token=eBMDTcG31VZzMTGFdnGBVnyyCyRFJLsDF12y8q8h2uQ')

  def test_sql_query_url(self):
    url = query_url_from_identifier('query:sql:48590282:146:_fA1xqpTf1cuDbLz-rGev3Lhy4CToixtMxzuszG54yE', api_base=self.api_base)
    self.assertEqual(url, self.api_base + '/48590282/stored_sql_query/146.json?resource_token=_fA1xqpTf1cuDbLz-rGev3Lhy4CToixtMxzuszG54yE')

  def test_invalid_query_id(self):
    with self.assertRaises(ValueError):
      url = query_url_from_identifier('query:48590200:21237:eBMDTcG31VZzMTGFdnGBVnyyCyRFJLsDF12y8q8h2uQ', api_base=self.api_base)

  # Contract URLs
  def test_contract_url_template(self):
    url_template = contract_url_template_from_identifier('contract:48590121:666570779:test', api_base=self.api_base)
    self.assertEqual(url_template, self.api_base + '/48590121/apps/666570779/data_contracts/contracts/test/{action}')

  def test_invalid_app_id(self):
    with self.assertRaises(ValueError):
      url = contract_url_template_from_identifier('contract:48590121:666570779:test:762m2n7yqyvjn4cdl2bfpgsid6x3h2a5', api_base=self.api_base)


if __name__ == '__main__':
  unittest.main()

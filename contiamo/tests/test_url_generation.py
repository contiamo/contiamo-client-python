import unittest

from contiamo.utils import query_url_from_identifier, contract_url_template_from_identifier
from contiamo.errors import InvalidRequestError


class IdentifierToUrl(unittest.TestCase):
    api_base = 'https://api.some-name.com'

    # Query URLs
    def test_query_url(self):
        url, token = query_url_from_identifier(
            'query:olap:48590200:21237:randomquerytoken', api_base=self.api_base)
        self.assertEqual(url, self.api_base +
                         '/48590200/published_queries/21237/data.json')
        self.assertEqual(token, 'randomquerytoken')

    def test_sql_query_url(self):
        url, token = query_url_from_identifier(
            'query:sql:48590282:146:randomquerytoken', api_base=self.api_base)
        self.assertEqual(url, self.api_base +
                         '/48590282/published_queries/146/data.json')

    def test_backward_compatible_query_url(self):
        url, token = query_url_from_identifier(
            'query:48590200:21237:randomquerytoken', api_base=self.api_base)
        self.assertEqual(url, self.api_base +
                         '/48590200/published_queries/21237/data.json')

    # Contract URLs
    def test_contract_url_template(self):
        url_template = contract_url_template_from_identifier(
            'contract:48590121:666570779:test', api_base=self.api_base)
        self.assertEqual(
            url_template, self.api_base + '/48590121/apps/666570779/data_contracts/contracts/test/{action}')

    def test_invalid_contract_id(self):
        with self.assertRaises(InvalidRequestError):
            contract_url_template_from_identifier(
                'contract:48590121:666570779:test:randomcontracttoken', api_base=self.api_base)


if __name__ == '__main__':
    unittest.main()

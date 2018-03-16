import responses
import unittest

from . import utils
from contiamo.resources import Client
from contiamo.public import query
from contiamo.data import DataClient
from contiamo.utils import query_url_from_identifier, contract_url_template_from_identifier
from contiamo.errors import (
    APIConnectionError, APIError, AuthenticationError, DataSourceError, NotFoundError, QueryError, ResponseError,
    UpdateError)


# the only meaningful parameter is api_base, which should not resolve
api_base = 'http://xyz.wrong-domain-name.123'
resource_id = '456'
contiamo_client = Client('some_api_key', api_base=api_base)
project = contiamo_client.Project(id='123')
resource = project.Dashboard(resource_id)

# resources module


def mock_erroneous_request(method, response_body, status, payload=None):
    url = resource.class_url() if method == 'create' else resource.instance_url()
    verb = {'retrieve': responses.GET, 'create': responses.POST, 'modify': responses.PUT}.get(method)
    responses.add(verb, url, body=response_body, status=status, content_type='application/json')

    argument = payload if payload else resource_id
    request_method = getattr(resource, method)
    request_method(argument)


def mock_erroneous_retrieve(response_body, status):
    mock_erroneous_request('retrieve', response_body, status)


def mock_erroneous_create(response_body, status):
    mock_erroneous_request('create', response_body, status, payload={'name': 'ResourceName'})


def mock_erroneous_update(response_body, status):
    mock_erroneous_request('modify', response_body, status, payload={'name': 'AnotherName'})

# public module


def mock_erroneous_query(response_body, status):
    query_id = 'query:olap:48590200:21237:randomquerytoken'
    query_url, token = query_url_from_identifier(query_id, api_base)
    responses.add(responses.GET, query_url, body=response_body, status=status, content_type='application/json')
    query(query_id, api_base=api_base)

# data module


def mock_erroneous_upload(response_body, status):
    contract_id = 'contract:48590121:666570779:test'
    contract_url = contract_url_template_from_identifier(contract_id, api_base).format(action='upload/process')
    responses.add(responses.POST, contract_url, body=response_body, status=status, content_type='application/json')
    data_client = DataClient(contract_id, 'contract_token', api_base=api_base)
    data_client.upload(filename=utils.file_test_data('mock_data.csv'))


class ErrorTestCase(unittest.TestCase):

    def test_connection_error(self):
        with self.assertRaises(APIConnectionError):
            resource.retrieve(resource_id)

    @responses.activate
    def test_auth_error(self):
        with self.assertRaises(AuthenticationError):
            mock_erroneous_retrieve('{"error":"not_found","logged_in":false}', 404)
        with self.assertRaises(AuthenticationError):
            mock_erroneous_retrieve('{"error":"server_error","logged_in":false}', 500)

    @responses.activate
    def test_notfound_error(self):
        with self.assertRaises(NotFoundError):
            mock_erroneous_retrieve('{"error":"not_found","logged_in":true}', 404)

    @responses.activate
    def test_api_error(self):
        with self.assertRaises(APIError):
            mock_erroneous_retrieve('{}', 500)

    @responses.activate
    def test_create_error(self):
        with self.assertRaises(UpdateError):
            mock_erroneous_create('{}', 422)

    @responses.activate
    def test_update_error(self):
        with self.assertRaises(UpdateError):
            mock_erroneous_update('{}', 409)
        with self.assertRaises(UpdateError):
            mock_erroneous_update('{}', 422)

    @responses.activate
    def test_invalid_response(self):
        with self.assertRaises(ResponseError):
            mock_erroneous_retrieve('{"invalid":"json"', 200)
        with self.assertRaises(ResponseError):
            mock_erroneous_upload('{"invalid":"json"', 200)
        with self.assertRaises(ResponseError):
            mock_erroneous_query('{"invalid":"json"', 200)

    @responses.activate
    def test_data_source_error(self):
        with self.assertRaises(DataSourceError):
            mock_erroneous_upload('{}', 412)
        with self.assertRaises(DataSourceError):
            mock_erroneous_query('{}', 412)

    @responses.activate
    def test_query_error(self):
        with self.assertRaises(QueryError):
            mock_erroneous_query('{}', 410)
        with self.assertRaises(QueryError):
            mock_erroneous_query('{}', 424)

    @responses.activate
    def test_include_error(self):
        error_message = 'This is an error message.'
        with self.assertRaises(UpdateError) as cm:
            mock_erroneous_update('{"error": "%s"}' % error_message, 409)
        self.assertTrue(error_message in str(cm.exception))


if __name__ == '__main__':
    unittest.main()

import unittest
import responses
import vcr

from contiamo.resources import *
from contiamo.public import query
from contiamo.errors import *


def instantiate_resource(api_key='apikey', api_base='https://api.base', project_id='123', resource_id='456'):
  contiamo_client = Client(api_key, api_base=api_base)
  project = contiamo_client.Project(project_id)
  resource = project.Dashboard(resource_id)
  return (resource, resource_id)

def make_erroneous_request(method, response_body, status, payload=None, **kwargs):
  resource, resource_id = instantiate_resource(**kwargs)

  url = resource.class_url() if method == 'create' else resource.instance_url()
  verb = {'retrieve': responses.GET, 'create': responses.POST, 'modify': responses.PUT}.get(method)
  responses.add(verb, url, body=response_body, status=status, content_type='application/json')

  argument = payload if payload else resource_id
  request_method = getattr(resource, method)
  request_method(argument)

def make_erroneous_retrieve(response_body, status, **kwargs):
  make_erroneous_request('retrieve', response_body, status, **kwargs)

def make_erroneous_create(response_body, status, **kwargs):
  make_erroneous_request('create', response_body, status, payload={'name': 'ResourceName'}, **kwargs)

def make_erroneous_update(response_body, status, **kwargs):
  make_erroneous_request('modify', response_body, status, payload={'name': 'AnotherName'}, **kwargs)

def make_erroneous_query(response_body, status):
  query_id = 'query:olap:48590200:21237:randomquerytoken'
  query_url = 'https://api.contiamo.com/48590200/stored_query/21237.json'
  responses.add(responses.GET, query_url, body=response_body, status=status, content_type='application/json')
  query(query_id)


class ErrorTestCase(unittest.TestCase):

  def test_connection_error(self):
    resource, resource_id = instantiate_resource(api_base='http://xyz.wrong-domain-name.123')
    with self.assertRaises(APIConnectionError):
      resource.retrieve(resource_id)

  @vcr.use_cassette('tests/cassettes/test_auth_error.yaml')
  def test_auth_error(self):
    resource, resource_id = instantiate_resource(api_key='wrong_api_key', api_base='https://api.contiamo.com')
    with self.assertRaises(AuthenticationError):
      resource.retrieve(resource_id)

  @responses.activate
  def test_notfound_error(self):
    with self.assertRaises(NotFoundError):
      make_erroneous_retrieve('{"error":"not_found","logged_in":true}', 404)

  @responses.activate
  def test_api_error(self):
    with self.assertRaises(APIError):
      make_erroneous_retrieve('{}', 500)

  @responses.activate
  def test_create_error(self):
    with self.assertRaises(UpdateError):
      make_erroneous_create('{}', 422)

  @responses.activate
  def test_update_error(self):
    with self.assertRaises(UpdateError):
      make_erroneous_update('{}', 409)
    with self.assertRaises(UpdateError):
      make_erroneous_update('{}', 422)

  @responses.activate
  def test_invalid_response(self):
    with self.assertRaises(ResponseError):
      make_erroneous_retrieve('{"invalid":"json"', 200)
    with self.assertRaises(ResponseError):
      make_erroneous_query('{"invalid":"json"', 200)

  @responses.activate
  def test_data_source_error(self):
    with self.assertRaises(DataSourceError):
      make_erroneous_query('{}', 412)
    # TODO: add data client error

  @responses.activate
  def test_query_error(self):
    with self.assertRaises(QueryError):
      make_erroneous_query('{}', 410)
    with self.assertRaises(QueryError):
      make_erroneous_query('{}', 424)


if __name__ == '__main__':
  unittest.main()

import unittest
import responses
import vcr

from contiamo.resources import *
from contiamo.public import query
from contiamo.errors import *


def instantiate_resource(api_key='apikey', api_base='https://api.base', project_id='123', dashboard_id='456'):
  contiamo_client = Client(api_key, api_base=api_base)
  project = contiamo_client.Project(project_id)
  dashboard = project.Dashboard(dashboard_id)
  return (dashboard, dashboard_id)

def make_erroneous_request(body, status, **kwargs):
  resource, resource_id = instantiate_resource(**kwargs)
  responses.add(responses.GET, resource.instance_url(), body=body, status=status, content_type='application/json')
  resource.retrieve(resource_id)

def make_erroneous_query(body, status):
  query_id = 'query:olap:48590200:21237:randomquerytoken'
  query_url = 'https://api.contiamo.com/48590200/stored_query/21237.json'
  responses.add(responses.GET, query_url, body=body, status=status, content_type='application/json')
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
      make_erroneous_request('{"error":"not_found","logged_in":true}', 404)

  @responses.activate
  def test_api_error(self):
    with self.assertRaises(APIError):
      make_erroneous_request('{}', 500)

  @responses.activate
  def test_invalid_response(self):
    with self.assertRaises(ResponseError):
      make_erroneous_request('{"invalid":"json"', 200)

  @responses.activate
  def test_data_source_error(self):
    with self.assertRaises(DataSourceError):
      make_erroneous_query('{}', 412)

  @responses.activate
  def test_query_error(self):
    with self.assertRaises(QueryError):
      make_erroneous_query('{}', 410)
    with self.assertRaises(QueryError):
      make_erroneous_query('{}', 424)

  @responses.activate
  def test_invalid_query_response(self):
    with self.assertRaises(ResponseError):
      make_erroneous_query('{"invalid":"json"', 200)


if __name__ == '__main__':
  unittest.main()

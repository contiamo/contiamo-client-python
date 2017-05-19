import unittest
import vcr

try:
  import pandas
except ImportError:
  pandas = None

from contiamo.resources import *

import yaml
import warnings

try:
  config = yaml.safe_load(open('tests/data/test_config.yml'))
  api_base = config['api_base']
  api_key = config['api_key']
  project_id = config['project_id']
  dashboard_id = config['dashboard_id']
  app_id = config['app_id']
  sql_table = config['sql_table']
except FileNotFoundError:
  warnings.warn('These tests will be skipped, as they require configuration information that is unavailable.')
  config = None


@unittest.skipIf(not config, 'Configuration information is not available.')
class ResourceTestCase(unittest.TestCase):

  client = Client(api_key, api_base=api_base)
  project = client.Project(project_id)
  dashboard = project.Dashboard.retrieve(dashboard_id)

  @vcr.use_cassette('tests/cassettes/test_retrieve.yaml')
  def test_retrieve(self):
    dashboard = self.project.Dashboard.retrieve(dashboard_id)
    self.assertTrue(isinstance(dashboard, self.project.Dashboard))
    self.assertEqual(dashboard['id'], dashboard_id)

  @vcr.use_cassette('tests/cassettes/test_retrieve.yaml')
  def test_fetch(self):
    dashboard = self.project.Dashboard(dashboard_id)
    dashboard.fetch()
    self.assertTrue(isinstance(dashboard, self.project.Dashboard))
    self.assertEqual(dashboard['id'], dashboard_id)

  @vcr.use_cassette('tests/cassettes/test_get_list.yaml')
  def test_get_list(self):
    dashboards = self.project.Dashboard.list()
    self.assertTrue(isinstance(dashboards[0], dict))
    dashboards = self.project.Dashboard.list(instantiate=True)
    self.assertTrue(isinstance(dashboards[0], self.project.Dashboard))

  @vcr.use_cassette('tests/cassettes/test_create.yaml')
  def test_create(self):
    dashboard_name = 'New dashboard'
    new_dashboard = self.project.Dashboard.create({'name': dashboard_name})
    self.assertTrue(isinstance(new_dashboard, self.project.Dashboard))
    self.assertEqual(new_dashboard['name'], dashboard_name)

  @vcr.use_cassette('tests/cassettes/test_modify.yaml')
  def test_modify(self):
    new_layout = 'report'
    response = self.dashboard.modify({'layout_type': new_layout})
    self.assertEqual(response['layout_type'], new_layout)

  @vcr.use_cassette('tests/cassettes/test_delete.yaml')
  def test_delete(self):
    dashboard = self.project.Dashboard(dashboard_id)
    widget = dashboard.Widget.create({"type":"text","left":8,"top":1,"width":15,"height":2,"title":"","description":""})
    response = widget.delete()
    # assume that if server returns {} without error then delete was successful
    self.assertEqual(len(response), 0)

  @vcr.use_cassette('tests/cassettes/test_sql_query.yaml')
  def test_sql_query(self):
    result = self.project.query_sql(app_id, 'select * from %s limit 2;' % sql_table)
    self.assertEqual(result.loc[0, 'field_a'], 1)

  # @TODO: add unit test for /data endpoints when API user is authorized


if __name__ == '__main__':
  unittest.main()

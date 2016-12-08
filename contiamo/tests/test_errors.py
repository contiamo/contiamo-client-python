import unittest

from contiamo.resources import *
from contiamo.errors import *


class ErrorTestCase(unittest.TestCase):

  def _make_erroneous_request(self, api_base, project_id, dashboard_id):
    contiamo_client = Client('token', api_base=api_base)
    project = contiamo_client.Project(project_id)
    dashboard = project.Dashboard.retrieve(dashboard_id)

  def test_connection_error(self):
    with self.assertRaises(APIConnectionError):
      self._make_erroneous_request('http://xyz.wrong-domain-name.123', '456', '789')

  # TODO: make cassette for other errors


if __name__ == '__main__':
  unittest.main()

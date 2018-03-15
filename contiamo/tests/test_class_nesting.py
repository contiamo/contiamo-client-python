import unittest

from contiamo.resources import CreateNestedResource, Client, Resource


class ClassNestingTestCase(unittest.TestCase):
    api_base = 'https://api.some-name.com'
    project_id = '123456'
    dashboard_id = '456789'

    def setUp(self):
        self.contiamo_client = Client('token', api_base=self.api_base)
        self.project = self.contiamo_client.Project(self.project_id)
        self.dashboard = self.project.Dashboard(self.dashboard_id)

    def test_nested_urls(self):
        self.assertEqual(self.project.instance_url(), '%s/%s' %
                         (self.api_base, self.project_id))
        self.assertEqual(self.dashboard.instance_url(), '%s/%s/%s' %
                         (self.project.instance_url(), 'dashboards', self.dashboard_id))

    def test_client(self):
        self.assertIs(self.dashboard.client(), self.contiamo_client.client())

    def test_nested_class_name(self):
        class ChildResource(Resource):
            pass

        class Parent(Resource):
            def _init_nested_resources(self):
                self.Child = CreateNestedResource(ChildResource, parent=self)
        parent = Parent('123456')
        self.assertEqual(parent.Child.__name__, 'ParentChild')


if __name__ == '__main__':
    unittest.main()

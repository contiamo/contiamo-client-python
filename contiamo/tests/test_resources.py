import vcr
import yaml

from . import utils
from contiamo.resources import Client


try:
    config = yaml.safe_load(open(utils.file_test_data('test_config.yml')))
except OSError:
    raise RuntimeError("Test config file not found. Email brandon@contiamo.com.")

api_base = config['api_base']
api_key = config['api_key']
project_id = config['project_id']
dashboard_id = config['dashboard_id']
app_id = config['app_id']
sql_table = config['sql_table']


class TestResources:

    client = Client(api_key, api_base=api_base)
    project = client.Project(project_id)
    dashboard = project.Dashboard.retrieve(dashboard_id)
    app = project.App(app_id)

    @vcr.use_cassette(utils.file_test_cassette('test_retrieve.yaml'))
    def test_retrieve(self):
        dashboard = self.project.Dashboard.retrieve(dashboard_id)
        assert isinstance(dashboard, self.project.Dashboard)
        assert dashboard['id'] == dashboard_id

    @vcr.use_cassette(utils.file_test_cassette('test_retrieve.yaml'))
    def test_fetch(self):
        dashboard = self.project.Dashboard(dashboard_id)
        dashboard.fetch()
        assert isinstance(dashboard, self.project.Dashboard)
        assert dashboard['id'] == dashboard_id

    @vcr.use_cassette(utils.file_test_cassette('test_get_list.yaml'))
    def test_get_list(self):
        dashboards = self.project.Dashboard.list()
        assert isinstance(dashboards[0], dict)
        dashboards = self.project.Dashboard.list(instantiate=True)
        assert isinstance(dashboards[0], self.project.Dashboard)

    @vcr.use_cassette(utils.file_test_cassette('test_create_dashboard.yaml'))
    def test_create_dashboard(self):
        dashboard_name = 'New dashboard'
        new_dashboard = self.project.Dashboard.create({'name': dashboard_name})
        assert isinstance(new_dashboard, self.project.Dashboard)
        assert new_dashboard['name'] == dashboard_name
        # Delete it so that we can create it next time
        new_dashboard.delete()

    @vcr.use_cassette(utils.file_test_cassette('test_create_contract.yaml'))
    def test_create_contract(self):
        contract_name = 'New contract'
        new_contract = self.app.Contract.create({'name': contract_name})
        assert isinstance(new_contract, self.app.Contract)
        assert new_contract['name'] == contract_name
        # Delete it so that we can create it next time
        new_contract.delete()

    @vcr.use_cassette(utils.file_test_cassette('test_modify.yaml'))
    def test_modify(self):
        new_layout = 'report'
        response = self.dashboard.modify({'layout_type': new_layout})
        assert response['layout_type'] == new_layout

    @vcr.use_cassette(utils.file_test_cassette('test_delete.yaml'))
    def test_delete(self):
        dashboard = self.project.Dashboard(dashboard_id)
        widget = dashboard.Widget.create(
            {"type": "text", "left": 8, "top": 1, "width": 15, "height": 2, "title": "", "description": ""})
        response = widget.delete()
        # assume that if server returns {} without error then delete was successful
        assert len(response) == 0

    @vcr.use_cassette(utils.file_test_cassette('test_sql_query.yaml'))
    def test_sql_query(self):
        result = self.project.query_sql(app_id, 'select * from %s limit 2;' % sql_table)
        assert result.loc[0, 'field_a'] == 1

    @vcr.use_cassette(utils.file_test_cassette('test_dynamic_query.yaml'))
    def test_dynamic_query(self):
        metric = "666571902:contract_data_value"
        dimension = "contract_data_category-category"
        payload = {
            "start_date": "2016-01", "end_date": "2016-01", "interval": "none", "period_unit": "month",
            "metrics": [{"key": metric}], "dimensions": [{"key": dimension}]
        }
        result = self.project.query(payload, use_column_names=False)
        assert metric in result and dimension in result

    # @TODO: add unit test for /data endpoints when API user is authorized

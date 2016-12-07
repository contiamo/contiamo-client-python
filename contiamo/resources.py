from .http_client import HTTPClient

import logging
logger = logging.getLogger(__name__)


def CreateNestedResource(base_class, parent, **kwargs):
  class_name = type(parent).__name__ + base_class.__name__.rstrip('Resource')
  logger.debug(class_name)
  properties = {'parent': parent}
  properties.update(kwargs)
  return type(class_name, (base_class,), properties)


###
# Main client
###
class Client:

  def __init__(self, api_key, api_base='https://api.contiamo.com'):
    self.api_key = api_key
    self.api_base = api_base
    self.http_client = HTTPClient(api_key)
    self.Project = CreateNestedResource(ProjectResource, parent=self, path_segment=None)

  def client(self):
    return self.http_client

  def instance_url(self):
    return self.api_base


###
# Base resource class
###
class Resource(dict):
  parent = None
  path_segment = None

  def __init__(self, id):
    self.id = id
    self._init_nested_resources()

  def _init_nested_resources(self):
    pass

  @classmethod
  def client(cls):
    return cls.parent.client()

  @classmethod
  def class_url(cls):
    base_url = cls.parent.instance_url()
    if cls.path_segment:
      return '%s/%s' % (base_url, cls.path_segment)
    else:
      return base_url

  def instance_url(self):
    # if not self.id:
    #   raise
    return '%s/%s' % (self.class_url(), self.id)

  @classmethod
  def list(cls, instantiate=False):
    response = cls.client().request('get', cls.class_url())
    result = response.json()
    if instantiate:
      resources = []
      for resource in result:
        resource_instance = cls(resource['id'])
        resource_instance.update(resource)
        resources.append(resource_instance)
      return resources
    else:
      return result

  @classmethod
  def retrieve(cls, id):
    instance = cls(id)
    instance.update(instance.request('get'))
    return instance

  def request(self, method):
    response = self.client().request('get', self.instance_url())
    return response.json()


###
# Resource classes
###
class ProjectResource(Resource):
  path_segment = 'projects'

  def _init_nested_resources(self):
    self.Dashboard = CreateNestedResource(DashboardResource, parent=self)
    self.App = CreateNestedResource(AppResource, parent=self)

class DashboardResource(Resource):
  path_segment = 'dashboards'

  def _init_nested_resources(self):
    self.Widget = CreateNestedResource(WidgetResource, parent=self)

class WidgetResource(Resource):
  path_segment = 'widgets'

class AppResource(Resource):
  path_segment = 'apps'

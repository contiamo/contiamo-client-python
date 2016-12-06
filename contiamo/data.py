import tempfile

from .http_client import HTTPClient
from .utils import logger, contract_url_template_from_identifier


class DataClient:

  def __init__(self, contract_id, token, api_base='https://api.contiamo.com'):
    self.api_base = api_base
    self.token = token
    self.url_template = contract_url_template_from_identifier(contract_id, api_base)
    self.client = HTTPClient()

  def _make_request(self, url, file_object=None):
    kwargs = {
      'params': {'access_token': self.token},
    }
    if file_object:
      kwargs.update({
        'files': {'file': file_object}
      })
    return self.client.request('post', url, **kwargs)

  def post_df(self, url, dataframe, ignore_index=True):
    # workaround until we can upload JSON data
    with tempfile.NamedTemporaryFile() as f:
      dataframe.to_csv(f.name, index=not(ignore_index))
      f.seek(0)
      result = self._make_request(url, f)
    return result

  def post_file(self, url, filename):
    with open(filename, 'rb') as f:
      result = self._make_request(url, f)
    return result

  def _post_data(self, url, dataframe, filename, ignore_index):
    if dataframe is None and filename is None:
      raise Exception('You need to specify at least a dataframe or a file to upload.')
    if dataframe is not None and filename is not None:
      raise Exception('Ambiguous request: You cannot provide both a dataframe and a file to upload.')

    if dataframe is not None:
      return self.post_df(url, dataframe, ignore_index)
    else:
      return self.post_file(url, filename)

  ###
  # Public methods
  def discover(self, dataframe=None, filename=None, ignore_index=True):
    url = self.url_template.format(action='upload/discover')
    return self._post_data(url, dataframe, filename, ignore_index)

  def upload(self, dataframe=None, filename=None, ignore_index=True):
    url = self.url_template.format(action='upload/process')
    return self._post_data(url, dataframe, filename, ignore_index)

  def purge(self):
    url = self.url_template.format(action='data_purge')
    return self._make_request(url)

import tempfile

try:
  import pandas
except ImportError:
  pandas = None

from contiamo.http_client import HTTPClient
from contiamo.utils import contract_url_template_from_identifier, raise_response_error
from contiamo.errors import InvalidRequestError

import logging
logger = logging.getLogger(__name__)


class DataClient:

  def __init__(self, contract_id, token, api_base='https://api.contiamo.com'):
    self.api_base = api_base
    self.token = token
    self.url_template = contract_url_template_from_identifier(contract_id, api_base)
    self.client = HTTPClient()

  def _make_request(self, url, file_object=None):
    kwargs = {'params': {'access_token': self.token}}
    if file_object:
      kwargs.update({'files': {'file-json': file_object}})

    response = self.client.request('post', url, **kwargs)
    try:
      json_response = response.json()
    except ValueError as e:  # JSONDecodeError inherits from ValueError
      raise_response_error(e, response, logger)

    return json_response

  def post_df(self, url, dataframe):
    with tempfile.NamedTemporaryFile() as f:
      dataframe.to_json(
        f.name, orient='records', lines=True, date_format='iso', date_unit='s'
      )

      f.seek(0)
      result = self._make_request(url, f)
    return result

  def post_file(self, url, filename):
    with open(filename, 'rb') as f:
      result = self._make_request(url, f)
    return result

  def _post_data(self, url, dataframe, filename):
    # sanity checks
    if dataframe is None and filename is None:
      raise InvalidRequestError('You need to specify at least a dataframe or a file to upload.')
    if dataframe is not None and filename is not None:
      raise InvalidRequestError('Ambiguous request: You cannot provide both a dataframe and a file to upload.')
    if dataframe is not None and not (pandas and isinstance(dataframe, pandas.DataFrame)):
      raise InvalidRequestError(
        'The argument you passed is a %s, not a pandas dataframe:\n%s' % (type(dataframe).__name__, str(dataframe)))

    if dataframe is not None:
      return self.post_df(url, dataframe)
    else:
      return self.post_file(url, filename)

  ###
  # Public methods
  def discover(self, dataframe=None, filename=None):
    url = self.url_template.format(action='upload/discover')
    return self._post_data(url, dataframe, filename)

  def upload(self, dataframe=None, filename=None):
    url = self.url_template.format(action='upload/process')
    return self._post_data(url, dataframe, filename)

  def purge(self):
    url = self.url_template.format(action='data_purge')
    return self._make_request(url)

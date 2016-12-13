try:
  import pandas as pd
  from .dateparser import DateParser
except ImportError:
  pd = None

from .http_client import HTTPClient
from .utils import query_url_from_identifier
from .errors import ResponseError

import logging
logger = logging.getLogger(__name__)


def _raise_response_error(e, response):
  logger.error('Invalid JSON response: %s' % response.text)
  raise ResponseError(
    'The JSON response from the server was invalid. Please report the bug to support@contiamo.com\n'
    'The following %s error was raised when parsing the JSON response:\n%s' % (type(e).__name__, e),
    http_body=response.content, http_status=response.status_code, headers=response.headers)

def _parse_json(json_response, parse_dates=True, use_column_names=True):
  df = pd.DataFrame()
  idx = 0
  try:
    for c in json_response['columns']:
      if use_column_names:
        col_name = c.get('name', 'Date')
      else:
        col_name = c['key']
      df[col_name] = [row[idx] for row in json_response['rows']]
      # Format
      if c['data_type'] == 'numeric':
        df[col_name] = pd.to_numeric(df[col_name])
        try:
          if df[col_name].dtype == 'float':
            # This function is not safe, it only works with floats.
            def is_integer(a):
              return a.is_integer()
            if df[col_name].map(is_integer).all():
              df[col_name] = df[col_name].astype(int)
        except Exception:
          pass  # really, we do not want this workaround to create any errors if it fails
      if c['data_type'] == 'date' and parse_dates and len(df[col_name]) > 0:
        parser = DateParser()
        parser.identifyPeriodUnit(df[col_name][0])
        df[col_name] = df[col_name].map(parser.parse)
      idx += 1
  except KeyError as e:
    _raise_response_error(e, response)
  return df

def query(query_id, parse_dates=True, use_column_names=True, row_limit=10000, api_base='https://api.contiamo.com'):
  http_client = HTTPClient()
  url = query_url_from_identifier(query_id, api_base)
  response = http_client.request('get', url)

  try:
    json_response = response.json()
  except ValueError as e:
    _raise_response_error(e, response)

  if pd:
    return _parse_json(json_response, parse_dates=parse_dates, use_column_names=use_column_names)
  else:
    return json_response

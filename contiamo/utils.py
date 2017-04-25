import os

try:
  import pandas as pd
  from contiamo.dateparser import DateParser
except ImportError:
  pd = None


###
# parse labs ids
def _raise_invalid_identifier_error(identifier, e):
  from contiamo.errors import InvalidRequestError
  raise InvalidRequestError(
    'The identifier "%s" is invalid. The following error was raised.\n'
    '%s: %s' % (identifier, type(e).__name__, e))

query_url_template = '{api_base}/{project_id}/published_queries/{query_id}/data.json'
def query_url_from_identifier(query_identifier, api_base):
  """query:query_type:project_id:query_id:token"""
  try:
    query_type, project_id, query_id, token = query_identifier.split(':')[1:]
  except ValueError as e:
    # backward compatibility
    try:
      project_id, query_id, token = query_identifier.split(':')[1:]
      query_type = 'olap'
    except ValueError as e:
      _raise_invalid_identifier_error(query_identifier, e)

  url = query_url_template.format(
    api_base=api_base,
    project_id=project_id,
    query_id=query_id)

  return url, token

contract_url_template = '{api_base}/{project_id}/apps/{app_id}/data_contracts/contracts/{contract_key}/{{action}}'
# escape curly braces to keep {action} in the template
def contract_url_template_from_identifier(contract_identifier, api_base):
  """contract:project_id:app_id:contract_key"""
  try:
    project_id, app_id, contract_key = contract_identifier.split(':')[1:]
  except ValueError as e:
    _raise_invalid_identifier_error(contract_identifier, e)

  return contract_url_template.format(
    api_base=api_base,
    project_id=project_id,
    app_id=app_id,
    contract_key=contract_key,
  )


###
# parse query response
def raise_json_error(e, response):
  from contiamo.errors import ResponseError
  raise ResponseError(
    'The JSON response from the server was invalid. Please report the bug to support@contiamo.com\n'
    'The following %s error was raised when parsing the JSON response:\n%s' % (type(e).__name__, e),
    json_body=response)

def parse_query_result(json_response, parse_dates=True, use_column_names=True):
  if not pd:
    return json_response

  # This function is not safe (only works with floats) so we keep it in the local namespace.
  def is_integer(a):
    return a.is_integer()

  df = pd.DataFrame()
  try:
    # parse column names and handle duplicates
    if use_column_names:
      column_names = []
      for column in json_response['columns']:
        if 'name' in column:
          column_names.append(column['name'])
        else:
          # column is a date, but can be the comparison date
          if column.get('comparison'):
            column_names.append('Date (comparison)')
          else:
            column_names.append('Date')
      if len(column_names) > len(set(column_names)):
        # column names not unique: use app_data name for metrics
        for idx, column in enumerate(json_response['columns']):
          if column['column_type'] == 'metric':
            column_names[idx] = column['app_data']['name'] + ': ' + column['name']
    else:
      column_names = [column['key'] for column in json_response['columns']]

    for idx, column in enumerate(json_response['columns']):
      col_name = column_names[idx]
      df[col_name] = [row[idx] for row in json_response['rows']]
      # Format
      if column['data_type'] == 'numeric':
        df[col_name] = pd.to_numeric(df[col_name])
        # try converting to integer if applicable
        try:
          if df[col_name].dtype == 'float':
            if df[col_name].map(is_integer).all():
              df[col_name] = df[col_name].astype(int)
        except Exception:
          pass  # really, we do not want this workaround to create any errors if it fails
      if parse_dates and column['data_type'] == 'date' and len(df[col_name]) > 0:
        parser = DateParser()
        parser.identifyPeriodUnit(df[col_name][0])
        df[col_name] = df[col_name].map(parser.parse)
  except KeyError as e:
    raise_json_error(e, json_response)
  return df

###
# misc
def raise_response_error(e, response, logger=None):
  from contiamo.errors import ResponseError
  if logger:
    logger.error('Invalid JSON response: %s' % response.text)
  raise ResponseError(
    'The JSON response from the server was invalid. Please report the bug to support@contiamo.com\n'
    'The following %s error was raised when parsing the JSON response:\n%s' % (type(e).__name__, e),
    http_body=response.content, http_status=response.status_code, headers=response.headers)

def get_file_extension(filename):
    _, ext = os.path.splitext(filename)
    return ext.lstrip('.')

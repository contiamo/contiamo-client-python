try:
  import pandas as pd
  from .dateparser import DateParser
except ImportError:
  pd = None


###
# parse labs ids
def _raise_invalid_identifier_error(identifier, e):
  from .errors import InvalidRequestError
  raise InvalidRequestError(
    'The identifier "%s" is invalid. The following error was raised.\n'
    '%s: %s' % (identifier, type(e).__name__, e))

query_url_template = '{api_base}/{project_id}/{path_segment}/{query_id}.json'
def query_url_from_identifier(query_identifier, api_base):
  """query:query_type:project_id:query_id:token"""
  try:
    query_type, project_id, query_id, token = query_identifier.split(':')[1:]
  except ValueError as e:
    _raise_invalid_identifier_error(query_identifier, e)

  url = query_url_template.format(
    api_base=api_base,
    project_id=project_id,
    path_segment=('stored_sql_query' if query_type == 'sql' else 'stored_query'),
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
def raise_response_error(e, response, logger=None):
  from .errors import ResponseError
  if logger:
    logger.error('Invalid JSON response: %s' % response.text)
  raise ResponseError(
    'The JSON response from the server was invalid. Please report the bug to support@contiamo.com\n'
    'The following %s error was raised when parsing the JSON response:\n%s' % (type(e).__name__, e),
    http_body=response.content, http_status=response.status_code, headers=response.headers)

def parse_query_result(json_response, parse_dates=True, use_column_names=True):
  if not pd:
    return json_response

  df = pd.DataFrame()
  try:
    for idx, c in enumerate(json_response['columns']):
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
  except KeyError as e:
    raise_response_error(e, response)
  return df

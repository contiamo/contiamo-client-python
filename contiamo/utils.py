def _raise_invalid_identifier_error(identifier, e):
  from contiamo.errors import InvalidRequestError
  raise InvalidRequestError(
    'The identifier "%s" is invalid. The following error was raised.\n'
    '%s: %s' % (identifier, type(e).__name__, e))

###
# parse query id
query_url = '{api_base}/{project_id}/{path_segment}/{query_id}.json?resource_token={token}'

def query_url_from_identifier(query_identifier, api_base):
  """query:query_type:project_id:query_id:token"""
  try:
    query_type, project_id, query_id, token = query_identifier.split(':')[1:]
  except ValueError as e:
    _raise_invalid_identifier_error(query_identifier, e)

  return query_url.format(
    api_base=api_base,
    project_id=project_id,
    path_segment=('stored_sql_query' if query_type == 'sql' else 'stored_query'),
    query_id=query_id,
    token=token
    )

###
# parse contract id
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

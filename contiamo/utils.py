import pandas as pd


###
# parse query id
query_url = '{api_base}/{project_id}/{path_segment}/{query_id}.json?resource_token={token}'

def query_url_from_identifier(query_identifier, api_base):
  """query:query_type:project_id:query_id:token"""
  try:
    query_type, project_id, query_id, token = query_identifier.split(':')[1:]
  except ValueError:
    raise  # invalid identifier

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
  except ValueError:
    raise  # invalid identifier

  return contract_url_template.format(
    api_base=api_base,
    project_id=project_id,
    app_id=app_id,
    contract_key=contract_key,
  )

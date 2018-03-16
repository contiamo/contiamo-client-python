from contiamo.http_client import HTTPClient
from contiamo.utils import query_url_from_identifier, parse_query_result, raise_response_error

import logging
logger = logging.getLogger(__name__)


def query(query_id, parse_dates=True, use_column_names=True, api_base='https://api.contiamo.com'):
    http_client = HTTPClient()
    url, token = query_url_from_identifier(query_id, api_base)
    response = http_client.request(
        'get', url, params={'resource_token': token})

    try:
        json_response = response.json()
    except ValueError as e:  # JSONDecodeError inherits from ValueError
        raise_response_error(e, response, logger)

    return parse_query_result(json_response, parse_dates=parse_dates, use_column_names=use_column_names)

import requests
from requests.exceptions import RequestException

from contiamo import errors

import logging
logger = logging.getLogger(__name__)


class HTTPClient:

  def __init__(self, api_key=None):
    self.api_key = api_key
    # verify_ssl_certs?
    # self._timeout = timeout

  def request(self, method, url, headers={}, **kwargs):
    logger.debug('Sending %s request to %s' % (method.upper(), url))
    headers.update({'Accept': 'application/json'})
    if self.api_key:
      headers.update({'X-API-TOKEN': self.api_key})

    try:
      response = requests.request(
        method,
        url,
        headers=headers,
        # data=post_data,
        # timeout=self._timeout,
        **kwargs)
    except TypeError as e:
      raise TypeError(
        'You most likely have an outdated requests library.\n'
        'The error message was: %s' % e)
    except RequestException as e:
      self._handle_request_error(e)

    if response.status_code != requests.codes.ok:
      self._handle_api_error(response)

    return response

  def _handle_request_error(self, e):
    # we may need to handle all exceptions, not just requests ones
    logger.error('%s connection error: %s' % (type(e).__name__, e))
    raise errors.APIConnectionError('The connection attempt raised the following %s error:\n%s' % (type(e).__name__, e))

  def _handle_api_error(self, response):
    logger.error('HTTP error %d: %s' % (response.status_code, response.text))
    is_auth_error = False
    try:
      is_auth_error = not response.json()['logged_in']
    except:
      pass
    if is_auth_error:
      raise errors.AuthenticationError(
        'Authentication failed, please check your credentials or contact us if the problem persists: support@contiamo.com\n'
        'The response from the server was: %s (HTTP error %d)' % (response.text, response.status_code),
        http_body=response.content, http_status=response.status_code, headers=response.headers)
    else:
      raise errors.APIError(
        'Invalid response from server (HTTP error %d): %s' % (response.status_code, response.text),
        http_body=response.content, http_status=response.status_code, headers=response.headers)

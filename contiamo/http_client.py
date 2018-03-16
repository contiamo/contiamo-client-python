import logging

import requests
from requests.exceptions import RequestException

from contiamo import errors


logger = logging.getLogger(__name__)


class HTTPClient:

    def __init__(self, api_key=None):
        self.api_key = api_key

    def request(self, method, url, headers=None, payload=None, **kwargs):
        logger.debug('Sending %s request to %s' % (method.upper(), url))
        if payload and logger.isEnabledFor(logging.DEBUG):
            logger.debug('With payload: ' + str(payload))

        if headers is None:
            headers = {}
        headers.update({'Accept': 'application/json'})
        if self.api_key:
            headers.update({'X-API-TOKEN': self.api_key})

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                json=payload,
                **kwargs)
        except (TypeError, RequestException) as e:
            self._handle_request_error(e)

        if response.status_code < 200 or response.status_code >= 300:
            self._handle_api_error(response)

        return response

    def _handle_request_error(self, e):
        if isinstance(e, TypeError):
            raise TypeError(
                'You most likely have an outdated version of the requests library. Try upgrading to the latest '
                'version.\nThe error message was: %s' % e)
        else:
            # we may need to handle all exceptions, not just requests ones
            logger.error('%s connection error: %s' % (type(e).__name__, e))
            raise errors.APIConnectionError(
                'The connection attempt raised the following %s error:\n%s' % (type(e).__name__, e))

    def _handle_api_error(self, response):
        logger.error('HTTP error %d: %s' %
                     (response.status_code, response.text))

        # check for authorization error first
        is_auth_error = False
        try:
            is_auth_error = not response.json()['logged_in']
        except (ValueError, KeyError):
            pass
        if is_auth_error:
            raise errors.AuthenticationError(
                http_body=response.content, http_status=response.status_code, headers=response.headers)

        ERROR_MAPPING = {
            404: errors.NotFoundError,
            412: errors.DataSourceError,
            410: errors.QueryError,
            424: errors.QueryError,
            409: errors.UpdateError,
            422: errors.UpdateError,
        }
        try:
            error_class = ERROR_MAPPING[response.status_code]
        except KeyError:
            error_class = errors.APIError  # catch all
        raise error_class(http_body=response.content, http_status=response.status_code, headers=response.headers)

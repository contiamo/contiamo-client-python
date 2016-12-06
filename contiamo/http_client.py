import requests

from .utils import logger


class HTTPClient:

  def __init__(self, api_key=None):
    self.api_key = api_key
    # verify_ssl_certs?
    # self._timeout = timeout

  def request(self, method, url, headers={}, **kwargs):
    logger.debug(url)
    if self.api_key:
      headers.update({'X-API-TOKEN': self.api_key})

    try:
      response = requests.request(method,
                                  url,
                                  headers=headers,
                                  # data=post_data,
                                  # timeout=self._timeout,
                                  **kwargs)
    except RequestException as e:
      raise Exception('The connection attempt raised the following error:\n%s' % e)

    if response.status_code != requests.codes.ok:
      logger.error('HTTP Error ' + str(response.status_code))
      logger.error(response.text)

    return response

import requests


class HTTPClient:

  def __init__(self, api_key):
    self.api_key = api_key
    # verify_ssl_certs?
    # self._timeout = timeout

  def request(self, method, url, headers={}, **kwargs):
    print(url)
    headers.update({'X-API-TOKEN': self.api_key})
    response = requests.request(method,
                                url,
                                headers=headers,
                                # data=post_data,
                                # timeout=self._timeout,
                                **kwargs)
    return response

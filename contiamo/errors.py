# Exceptions
import sys


class ContiamoException(Exception):
  """Base class for the library's errors."""
  default_message = None

  def __init__(self, message=None, http_body=None, http_status=None, json_body=None, headers=None):
    error_message = message if message else self.default_message
    super().__init__(error_message)

    # if bytes, decode to string
    if http_body and hasattr(http_body, 'decode'):
      try:
        http_body = http_body.decode('utf-8')
      except BaseException:
        http_body = ('<Could not decode body as utf-8. Please report to support@contiamo.com>')

    self.http_body = http_body
    self.http_status = http_status
    self.json_body = json_body
    self.headers = headers or {}

  if sys.version_info < (3, 0):
    def __str__(self):
      return unicode(self).encode('utf-8')


class APIConnectionError(ContiamoException):
  """Basic connection errors such as server not responding."""
  pass

class AuthenticationError(ContiamoException):
  """Authentication error due to invalid credentials."""
  default_message = (
    'Authentication failed, please check your credentials (project id and API key) '
    'or contact us if the problem persists: support@contiamo.com')

class NotFoundError(ContiamoException):
  """Error raised when resource is not found after successful authentication."""
  default_message = 'The resource you requested was not found.'

class DataSourceError(ContiamoException):
  """Raises errors related to querying or updating data sources."""
  default_message = 'There was an error with the data source involved in your request.'

class UpdateError(ContiamoException):
  """Errors related to saving or updating resources."""
  default_message = 'An error happened while creating or updating the resource.'

class QueryError(ContiamoException):
  """Errors related to published query execution."""
  default_message = 'An error happened while executing the query.'

class APIError(ContiamoException):
  """Catch-all error for all other non-200 responses including 500."""
  default_message = 'The server responded with an unusual error. Please retry or report the bug to support@contiamo.com'

class ResponseError(ContiamoException):
  """Raised for invalid responses (e.g. invalid JSON); should be rare."""
  default_message = 'The JSON response from the server was invalid. Please report the bug to support@contiamo.com'

class InvalidRequestError(ContiamoException):
  """Invalid request errors caught before sending the request."""
  pass

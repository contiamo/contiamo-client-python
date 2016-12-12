# Exceptions
import sys


class ContiamoException(Exception):
  """Base class for the library's errors."""

  def __init__(self, message=None, http_body=None, http_status=None, json_body=None, headers=None):
    super().__init__(message)

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
  pass

class NotFoundError(ContiamoException):
  """Error raised when resource is not found after successful authentication."""
  pass

class ResponseError(ContiamoException):
  """Raised for invalid responses (e.g. invalid JSON); should be rare."""
  pass

class APIError(ContiamoException):
  """Catch-all error for all other non-200 responses including 500."""
  pass

class InvalidRequestError(ContiamoException):
  """Invalid request errors caught before sending the request."""
  pass

from dataclasses import dataclass, field
from functools import partial
from posixpath import join
from typing import Callable, Dict, Optional

from requests import Response, Session

# -- API Endpoint
_API_ENDPOINT = 'https://www.opensubtitles.com/api'

# -- API Version
_API_VERSION = 'v1'


def _call_api(request: Callable[[str, ...], Response], operation: str, **kwargs) -> Dict:
    """
    Calls a specific operation on the OpenSubtitles API

    :param request: Function responsible for sending an HTTP Request
    :param operation: The API operation to call
    :param kwargs: The operation arguments
    :return: The operation's response
    """
    with request(join(_API_ENDPOINT, _API_VERSION, operation), **kwargs) as response:
        # Return parsed response
        return response.json()


def _get(session: Session, operation: str, timeout=None, **kwargs) -> Dict:
    """
    Calls a specific operation on the OpenSubtitles API using HTTP GET

    :param session: The current HTTP session
    :param operation: The API operation to call
    :param timeout: The timeout for the call
    :param kwargs: The operation arguments
    :return: The operation's response
    """
    return _call_api(session.get, operation, timeout=timeout, params=kwargs)


def _post(session: Session, operation: str, timeout=None, **kwargs) -> Dict:
    """
    Calls a specific operation on the OpenSubtitles API using HTTP POST

    :param session: The current HTTP session
    :param operation: The API operation to call
    :param timeout: The timeout for the call
    :param kwargs: The operation arguments
    :return: The operation's response
    """
    return _call_api(session.post, operation, timeout=timeout, data=kwargs)


@dataclass(frozen=True)
class ApiOperation:
    """
    Represents an OpenSubtitles API Operation

    :param execute: The function that makes the actual API call.
                    This is a required parameter.
    :param name: The actual operation's name, as per their documentation.
                 This is a required parameter.
    :param callback: A function to call once a response is obtained from the API call.
                     This is an optional parameter.
    :param void: Whether or not to return the response to the caller.
                 This is an optional parameter.
    """
    execute: Callable[[Session, str, ...], Dict]
    name: str
    callback: Callable[[Dict, Session], Dict] = field(default=lambda data, *_: data)
    void: bool = field(default=False)

    def __call__(self, session: Session, **kwargs) -> Optional[Dict]:
        response = self.callback(self.execute(session, self.name, timeout=kwargs.pop('timeout'), **kwargs), session)
        return None if self.void else response


# -- Some helper wrappers
GET = partial(ApiOperation, _get)
POST = partial(ApiOperation, _post)

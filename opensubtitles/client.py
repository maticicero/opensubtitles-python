from functools import partial
from typing import Any, Dict, Union

from requests import Session

from .auth import ApiAuthentication
from .operations import ApiOperation, GET, POST


class OpenSubtitlesClient:
    """
    A low-level client for the OpenSubtitles API

    :param api_key: The API Key identifies the consumer of the API.
                    This is a required parameter.
    :param timeout: Timeout (in seconds) until an API call is aborted.
                    This is an optional parameter. Default is 5 seconds.
    """

    # -- User Agent for this Client
    _USER_AGENT = 'OpenSubtitles-Python'

    _session: Session
    _timeout: int

    def __init__(self, api_key: str, timeout=5):
        self._session = self._new_session(api_key)
        self._timeout = timeout

    def __getattribute__(self, attr: str) -> Any:
        value: Union[ApiOperation, Any] = super().__getattribute__(attr)
        if isinstance(value, ApiOperation):
            return partial(value, self._session, timeout=self._timeout)
        return value

    @classmethod
    def _new_session(cls, api_key: str) -> Session:
        session = Session()
        session.headers.update({
            'User-Agent': cls._USER_AGENT
        })
        session.auth = ApiAuthentication(api_key)
        return session

    def close(self) -> None:
        """
        Closes all the resources held by this client
        """
        self._session.close()


def _on_login(data: Dict, session: Session, *_, **__):
    session.auth = ApiAuthentication(session.auth.api_key, data['token'])
    return data


# -- API Operations
OpenSubtitlesClient.login = POST('login', callback=_on_login, void=True)
OpenSubtitlesClient.subtitles = GET('subtitles')

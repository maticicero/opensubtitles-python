from dataclasses import dataclass, field
from posixpath import join
from typing import Any, Callable, Dict, Optional, Union

from requests import Session, Request, Response
from requests.auth import AuthBase


@dataclass(frozen=True)
class ApiAuthentication(AuthBase):
    api_key: str
    token: Optional[str] = field(default=None)

    def __call__(self, request: Request) -> Request:
        request.headers['Api-Key'] = self.api_key
        if self.token:
            request.headers['Authentication'] = f'Bearer {self.token}'
        return request


_API_ENDPOINT = 'https://www.opensubtitles.com/api'
_API_VERSION = 'v1'


def execute_api_operation(method: Callable[[str, ...], Response], operation: str, **kwargs) -> Dict:
    timeout = kwargs.pop('_timeout', None)
    with method(join(_API_ENDPOINT, _API_VERSION, operation), timeout=timeout, **kwargs) as response:
        return response.json()


def GET(session: Session, operation: str, **kwargs) -> Dict:
    return execute_api_operation(session.get, operation, params=kwargs)


def POST(session: Session, operation: str, **kwargs) -> Dict:
    return execute_api_operation(session.post, operation, data=kwargs)


@dataclass(frozen=True)
class ApiOperation:
    method: Callable[[Session, str, ...], Dict]
    name: str
    callback: Optional[Callable[[Dict, Session], Dict]] = field(default=None)
    void: bool = field(default=False)


class OpenSubtitlesClient:
    _USER_AGENT = 'OpenSubtitles-Python'

    _session: Session
    _timeout: int

    def __init__(self, api_key: str, timeout=5):
        self._session = self._new_session(api_key)
        self._timeout = timeout

    def __getattribute__(self, attr: str) -> Any:
        value: Union[ApiOperation, Any] = super().__getattribute__(attr)
        if isinstance(value, ApiOperation):
            operation = value

            def _operation(**kwargs):
                response = operation.method(self._session, operation.name, _timeout=self._timeout, **kwargs)
                response = operation.callback(response, self._session) if operation.callback else response
                return None if operation.void else response

            return _operation
        return value

    @classmethod
    def _new_session(cls, api_key: str) -> Session:
        session = Session()
        session.headers.update({
            'User-Agent': cls._USER_AGENT
        })
        session.auth = ApiAuthentication(api_key)
        return session

    def close(self):
        self._session.close()


def _on_login(data: Dict, session: Session, *_, **__):
    session.auth = ApiAuthentication(session.auth.api_key, data['token'])
    return data


# -- API Operations
OpenSubtitlesClient.login = ApiOperation(POST, 'login', callback=_on_login, void=True)
OpenSubtitlesClient.subtitles = ApiOperation(GET, 'subtitles')

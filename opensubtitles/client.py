from functools import partial, reduce
from json import JSONDecodeError
from requests import PreparedRequest, Request, Response, Session
from typing import Callable, Type

from .auth import ApiAuthentication
from .exceptions import ApiException

_ENDPOINT = 'https://www.opensubtitles.com'

class ApiOperation:

    _session: Session
    _name: str
    _method: str
    _timeout: int
    _request_interceptors: list[Callable[[Request], Request]]
    _response_interceptors: list[Callable[[Response], Response]]
    _post_callback: Callable[[dict], None]
    _void: bool

    def __init__(self, session: Session, name: str, method: str = 'GET', timeout: int = 5):
        self._session = session
        self._name = name
        self._method = method
        self._timeout = timeout
        self._request_interceptors = []
        self._response_interceptor = []
        self._void = False
    
    @staticmethod
    def _parse_response(response: Response) -> dict:
            try:
                data = response.json()
            except JSONDecodeError as e:
                raise ApiException(response.status_code) from e
            if not response.ok:
                raise ApiException(data['status'], data.get('errors') or data.get('message'))
            return data

    def _execute(self, data: dict) -> dict:
        request: PreparedRequest = reduce(lambda req, intercept: intercept(req), self._request_interceptors, Request(
            self._method, f'{_ENDPOINT}/api/v1/{self._name}',
            data=data, auth=self._session.auth, headers=self._session.headers
        )).prepare()
        with self._session.send(request, timeout=self._timeout) as response:
            response: Response = reduce(lambda resp, intercept: intercept(resp), self._response_interceptor, response)
            content = self._parse_response(response)
            self._post_callback(content)
            return None if self._void else content
    
    def __call__(self, **data) -> dict:
        return self._execute(data)
    
    def with_request_interceptor(self, interceptor: Callable[[Request], Request]) -> 'ApiOperation':
        self._request_interceptors.append(interceptor)
        return self

    def with_response_interceptor(self, interceptor: Callable[[Response], Response]) -> 'ApiOperation':
        self._response_interceptors.append(interceptor)
        return self
    
    def do_after(self, callback: Callable[[dict], None]) -> 'ApiOperation':
        self._post_callback = callback
        return self
    
    def no_response(self) -> 'ApiOperation':
        self._void = True
        return self

class OpenSubtitlesClient:

    _session: Session

    # -- API Operations
    login: ApiOperation
    subtitles: ApiOperation

    def __init__(self, api_key: str):
        self._init_session()
        self._init_operations()
        self._session.auth = ApiAuthentication(api_key)
    
    def _init_session(self):
        self._session = Session()
        self._session.headers.update({
            'Content-Type': 'multipart/form-data',
            'User-Agent': 'OpenSubtitles-Python'
        })
    
    def _init_operations(self):
        api_operation = partial(ApiOperation, self._session)
        self.login = api_operation('login', 'POST').do_after(self._on_login).no_response()
        self.subtitles = api_operation('subtitles', 'GET')
    
    def _on_login(self, data: dict):
        self._session.auth = ApiAuthentication(self._session.auth.api_key, data['token'])
    
    def close(self):
        self._session.close()

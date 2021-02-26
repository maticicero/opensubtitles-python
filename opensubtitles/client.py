from requests import Session
from json import JSONDecodeError

from .auth import ApiAuthentication
from .exceptions import ApiException

class OpenSubtitlesClient:

    _ENDPOINT = 'https://www.opensubtitles.com'

    _session: Session

    def __init__(self, api_key: str):
        self._init_session()
        self._session.auth = ApiAuthentication(api_key)
    
    def _init_session(self):
        self._session = Session()
        self._session.headers.update({
            'Content-Type': 'multipart/form-data',
            'User-Agent': 'OpenSubtitles-Python'
        })
    
    def _request(self, operation: str, method: str, **kwargs) -> dict:
        with getattr(self._session, method)(f'{self._ENDPOINT}/api/v1/{operation}', **kwargs) as response:
            try:
                data = response.json()
            except JSONDecodeError:
                data = dict(status=response.status_code)
            if not response.ok:
                raise ApiException(data)
            return data


    def login(self, username: str, password: str) -> None:
        response = self._request('login', 'post', data={ 'username': username, 'password': password })
        self._session.auth = ApiAuthentication(self._session.auth.api_key, response['token'])
    
    def close(self):
        self._session.close()

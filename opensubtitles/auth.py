from dataclasses import dataclass, field
from typing import Optional

from requests import Request
from requests.auth import AuthBase


@dataclass(frozen=True)
class ApiAuthentication(AuthBase):
    """
    Provides authentication for OpenSubtitles API.
    More information on https://opensubtitles.stoplight.io/docs/opensubtitles-api/open_api.json#authentication

    :param api_key: The API Key identifies the consumer of the API.
                    This is a required parameter.
    :param token: The token identifies a specific user of OpenSubtitles.
                  This is an optional parameter.
    """
    api_key: str
    token: Optional[str] = field(default=None)

    def __call__(self, request: Request) -> Request:
        request.headers['Api-Key'] = self.api_key
        if self.token:
            request.headers['Authentication'] = f'Bearer {self.token}'
        return request

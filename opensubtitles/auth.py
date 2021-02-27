import attr
from requests import Request
from requests.auth import AuthBase
from typing import Optional

@attr.s(frozen=True)
class ApiAuthentication(AuthBase):

    api_key: str = attr.ib(
        validator=attr.validators.instance_of(str),
        repr=lambda key: f'{key[:5]}{"*" * len(key[:5])}'
    )
    token: Optional[str] = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(str)),
        repr=False
    )

    def __call__(self, request: Request) -> Request:
        request.headers['Api-Key'] = self.api_key
        if self.token:
            request.headers['Authentication'] = f'Bearer {self.token}'
        return request

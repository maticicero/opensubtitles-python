import attr

from typing import Optional

@attr.s(frozen=True)
class ApiException(Exception):
    code: int = attr.ib(
        validator=attr.validators.instance_of(int)
    )
    reason: Optional[str] = attr.ib(
        default=None,
        converter=str,
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )

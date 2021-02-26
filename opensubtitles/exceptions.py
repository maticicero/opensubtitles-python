from typing import Optional

class ApiException(Exception):
    code: int
    reason: Optional[str]

    def __init__(self, response: dict):
        self.code = response['status']
        self.reason = str(response.get('errors', '')) or response.get('message')
        super().__init__(f'HTTP {self.code} - {self.reason}')

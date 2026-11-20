"""Small standard-library HTTP client used by CLI, replay, and tests."""
import json
import urllib.error
import urllib.request
from typing import Any


def request(base_url: str, path: str, *, token: str | None = None,
            body: dict[str, Any] | None = None, timeout: float = 3.0) -> tuple[int, dict[str, Any] | str]:
    headers: dict[str, str] = {}
    if token:
        headers['X-Lab-Token'] = token
    data = None
    if body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(base_url + path, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            code, text = res.status, res.read(65536).decode('utf-8')
    except urllib.error.HTTPError as err:
        code, text = err.code, err.read(65536).decode('utf-8')
    try:
        return code, json.loads(text)
    except json.JSONDecodeError:
        return code, text

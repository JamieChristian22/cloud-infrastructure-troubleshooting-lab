"""Minimal observability-enabled service for reproducible failures and recoveries."""
import hmac
import json
import logging
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

from .state import FAULTS, RuntimeState

LOG = logging.getLogger('cloudops_lab')
ORDERS = [
    {'id': 'SAMPLE-1001', 'status': 'fulfilled', 'amount_usd': 48.50},
    {'id': 'SAMPLE-1002', 'status': 'processing', 'amount_usd': 17.25},
]


class LabHandler(BaseHTTPRequestHandler):
    server_version = 'CloudOpsLab/1.0'
    sys_version = ''

    def log_message(self, format: str, *args: Any) -> None:
        # No default access log: it can contain user-supplied strings and tokens.
        return

    def _route(self) -> str:
        path = urlsplit(self.path).path
        return path if path in {'/', '/health/live', '/health/ready', '/api/orders', '/metrics', '/ops/state', '/ops/fault'} else '/not-found'

    def _authorized(self) -> bool:
        presented = self.headers.get('X-Lab-Token', '')
        return bool(presented) and hmac.compare_digest(presented, self.server.lab_token)  # type: ignore[attr-defined]

    def _reply(self, code: int, payload: Any, *, content_type: str = 'application/json; charset=utf-8') -> None:
        raw = payload.encode('utf-8') if isinstance(payload, str) else json.dumps(payload, sort_keys=True).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Request-ID', self.request_id)
        self.end_headers()
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _begin(self) -> float:
        self.request_id = str(uuid4())
        return time.monotonic()

    def _finish(self, start: float, code: int) -> None:
        elapsed = time.monotonic() - start
        route = self._route()
        self.server.runtime.record(route, code, elapsed)  # type: ignore[attr-defined]
        LOG.info(json.dumps({'event': 'http_request', 'request_id': self.request_id,
                             'method': self.command, 'route': route, 'status': code,
                             'elapsed_ms': round(elapsed * 1000, 2)}))

    def do_GET(self) -> None:
        start = self._begin()
        route = self._route()
        runtime: RuntimeState = self.server.runtime  # type: ignore[attr-defined]
        fault = runtime.fault
        code = 200
        if route == '/':
            payload = {'service': 'CloudOps Incident Lab', 'mode': 'local simulation',
                       'endpoints': ['/health/live', '/health/ready', '/api/orders', '/metrics']}
        elif route == '/health/live':
            payload = {'status': 'alive'}
        elif route == '/health/ready':
            code = 503 if fault == 'dependency_outage' else 200
            payload = {'status': 'not_ready' if code == 503 else 'ready', 'dependency': 'unavailable' if code == 503 else 'available'}
        elif route == '/api/orders':
            if fault == 'high_latency':
                time.sleep(0.30)
            code = {'dependency_outage': 503, 'application_error': 500, 'auth_misconfig': 401}.get(fault, 200)
            payload = ({'orders': ORDERS, 'data_classification': 'synthetic'} if code == 200
                       else {'error': {503: 'dependency_unavailable', 500: 'application_failure',
                                      401: 'upstream_authentication_failed'}[code]})
        elif route == '/metrics':
            self._reply(200, runtime.prometheus(), content_type='text/plain; version=0.0.4; charset=utf-8')
            self._finish(start, 200)
            return
        elif route == '/ops/state':
            code = 200 if self._authorized() else 403
            payload = runtime.snapshot() if code == 200 else {'error': 'forbidden'}
        else:
            code, payload = 404, {'error': 'not_found'}
        self._reply(code, payload)
        self._finish(start, code)

    def do_POST(self) -> None:
        start = self._begin()
        route = self._route()
        code = 404
        payload: dict[str, Any] = {'error': 'not_found'}
        if route == '/ops/fault':
            if not self._authorized():
                code, payload = 403, {'error': 'forbidden'}
            else:
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                    if not 0 < length <= 1024:
                        raise ValueError('invalid content length')
                    body = json.loads(self.rfile.read(length))
                    value = body.get('fault') if isinstance(body, dict) else None
                    if value not in FAULTS:
                        raise ValueError('unsupported fault')
                    self.server.runtime.set_fault(value)  # type: ignore[attr-defined]
                    code, payload = 200, {'fault': value, 'changed': True}
                except (ValueError, json.JSONDecodeError, TypeError):
                    code, payload = 400, {'error': 'invalid_fault_request', 'allowed': FAULTS}
        self._reply(code, payload)
        self._finish(start, code)


def build_server(host: str = '127.0.0.1', port: int = 0, *, token: str, state: RuntimeState | None = None) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), LabHandler)
    server.daemon_threads = True
    server.runtime = state or RuntimeState()  # type: ignore[attr-defined]
    server.lab_token = token  # type: ignore[attr-defined]
    return server

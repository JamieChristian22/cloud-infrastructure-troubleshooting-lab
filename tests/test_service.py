"""Contract, failure, recovery, auth, and telemetry tests."""
import secrets
import threading
import time
import unittest
from urllib.request import Request, urlopen

from cloudops_lab.client import request
from cloudops_lab.server import build_server
from cloudops_lab.state import RuntimeState


class ServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.token = secrets.token_urlsafe(18)
        cls.server = build_server(token=cls.token)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def tearDown(self) -> None:
        request(self.base, '/ops/fault', token=self.token, body={'fault': 'none'})

    def test_healthy_by_default(self) -> None:
        self.assertEqual(request(self.base, '/health/live')[0], 200)
        self.assertEqual(request(self.base, '/health/ready')[0], 200)
        status, body = request(self.base, '/api/orders')
        self.assertEqual(status, 200)
        self.assertEqual(body['data_classification'], 'synthetic')

    def test_dependency_failure_propagates_to_readiness(self) -> None:
        request(self.base, '/ops/fault', token=self.token, body={'fault': 'dependency_outage'})
        self.assertEqual(request(self.base, '/health/live')[0], 200)
        self.assertEqual(request(self.base, '/health/ready')[0], 503)
        self.assertEqual(request(self.base, '/api/orders')[0], 503)
        request(self.base, '/ops/fault', token=self.token, body={'fault': 'none'})
        self.assertEqual(request(self.base, '/health/ready')[0], 200)

    def test_application_failure_and_recovery(self) -> None:
        request(self.base, '/ops/fault', token=self.token, body={'fault': 'application_error'})
        self.assertEqual(request(self.base, '/api/orders')[0], 500)
        request(self.base, '/ops/fault', token=self.token, body={'fault': 'none'})
        self.assertEqual(request(self.base, '/api/orders')[0], 200)

    def test_auth_misconfig_scenario(self) -> None:
        request(self.base, '/ops/fault', token=self.token, body={'fault': 'auth_misconfig'})
        self.assertEqual(request(self.base, '/api/orders')[0], 401)

    def test_high_latency_scenario(self) -> None:
        request(self.base, '/ops/fault', token=self.token, body={'fault': 'high_latency'})
        start = time.monotonic()
        self.assertEqual(request(self.base, '/api/orders')[0], 200)
        self.assertGreaterEqual(time.monotonic() - start, 0.25)

    def test_fault_management_requires_token(self) -> None:
        self.assertEqual(request(self.base, '/ops/state')[0], 403)
        self.assertEqual(request(self.base, '/ops/fault', body={'fault': 'dependency_outage'})[0], 403)
        self.assertEqual(request(self.base, '/ops/fault', token='wrong', body={'fault': 'dependency_outage'})[0], 403)
        self.assertEqual(request(self.base, '/ops/state', token=self.token)[0], 200)
        self.assertEqual(request(self.base, '/health/ready')[0], 200)

    def test_unknown_fault_is_rejected(self) -> None:
        self.assertEqual(request(self.base, '/ops/fault', token=self.token, body={'fault': 'delete_all'})[0], 400)
        self.assertEqual(request(self.base, '/health/ready')[0], 200)

    def test_no_unbounded_route_labels(self) -> None:
        self.assertEqual(request(self.base, '/unrecognized/url?token=secret')[0], 404)
        code, state = request(self.base, '/ops/state', token=self.token)
        self.assertEqual(code, 200)
        self.assertTrue(any(x['route'] == '/not-found' for x in state['recent_events']))

    def test_metrics_and_request_id(self) -> None:
        with urlopen(Request(self.base + '/health/live'), timeout=3) as resp:
            self.assertTrue(resp.headers['X-Request-ID'])
        code, metrics = request(self.base, '/metrics')
        self.assertEqual(code, 200)
        self.assertIn('lab_requests_total', metrics)
        self.assertIn('lab_request_duration_seconds_sum', metrics)


class StateTests(unittest.TestCase):
    def test_empty_and_recorded_state(self) -> None:
        state = RuntimeState()
        self.assertEqual(state.snapshot()['requests_total'], 0)
        state.record('/health/live', 200, 0.012)
        state.record('/health/live', 503, 0.021)
        self.assertEqual(state.snapshot()['requests_total'], 2)
        self.assertEqual(state.snapshot()['status_counts'], {'200': 1, '503': 1})

    def test_valid_faults_only(self) -> None:
        state = RuntimeState()
        with self.assertRaises(ValueError):
            state.set_fault('unknown')
        self.assertEqual(state.fault, 'none')

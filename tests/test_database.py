"""Test actual SQLite dependency failure and recovery, plus histogram semantics."""
import secrets
import threading
import unittest

from cloudops_lab.client import request
from cloudops_lab.database import DatabaseUnavailable, OrdersDatabase
from cloudops_lab.server import build_server
from cloudops_lab.state import RuntimeState


class DatabaseUnitTests(unittest.TestCase):
    def test_seeded_query_and_real_disconnect(self):
        db = OrdersDatabase()
        self.assertTrue(db.ready())
        self.assertEqual(len(db.list_orders()), 2)
        db.disconnect()
        self.assertFalse(db.ready())
        with self.assertRaises(DatabaseUnavailable):
            db.list_orders()
        db.recover()
        self.assertTrue(db.ready())
        self.assertEqual(db.list_orders()[0]['id'], 'SAMPLE-1001')
        db.close()

    def test_recovery_is_idempotent(self):
        db = OrdersDatabase()
        db.recover()
        self.assertEqual(len(db.list_orders()), 2)
        db.close()

    def test_histogram_buckets_are_cumulative(self):
        state = RuntimeState()
        state.record('/api/orders', 200, 0.020)
        state.record('/api/orders', 200, 0.350)
        metrics = state.prometheus()
        self.assertIn('lab_request_duration_histogram_seconds_bucket{route="/api/orders",le="0.025"} 1', metrics)
        self.assertIn('lab_request_duration_histogram_seconds_bucket{route="/api/orders",le="0.5"} 2', metrics)
        self.assertIn('lab_request_duration_histogram_seconds_bucket{route="/api/orders",le="+Inf"} 2', metrics)
        self.assertIn('lab_request_duration_histogram_seconds_count{route="/api/orders"} 2', metrics)


class DatabaseHTTPTests(unittest.TestCase):
    def test_readiness_and_orders_follow_actual_sqlite_connection(self):
        server = build_server(token=secrets.token_urlsafe(24))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            self.assertEqual(request(base, '/health/ready')[0], 200)
            server.orders_db.disconnect()
            self.assertEqual(request(base, '/health/live')[0], 200)
            self.assertEqual(request(base, '/health/ready')[0], 503)
            self.assertEqual(request(base, '/api/orders')[0], 503)
            server.orders_db.recover()
            self.assertEqual(request(base, '/health/ready')[0], 200)
            self.assertEqual(request(base, '/api/orders')[0], 200)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

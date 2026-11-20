import tempfile
import unittest
from pathlib import Path

from cloudops_lab.triage import linux_snapshot, network_snapshot


class TriageTests(unittest.TestCase):
    def test_system_report_local_only(self) -> None:
        with tempfile.TemporaryDirectory() as path:
            result = linux_snapshot(path)
            self.assertGreater(result['disk']['total_bytes'], 0)
            self.assertIn('read-only', result['scope'])
            self.assertGreater(result['cpu_count'], 0)

    def test_dns_resolution(self) -> None:
        result = network_snapshot('localhost', 9, timeout=0.1)
        self.assertTrue(result['dns_resolved'])
        self.assertEqual(result['port'], 9)

    def test_invalid_host_cannot_resolve(self) -> None:
        # Test avoids external DNS (empty host is invalid on supported OSes).
        result = network_snapshot('', 8080, timeout=0.1)
        self.assertFalse(result['tcp_connected'])

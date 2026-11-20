"""The public replay workflow must produce actual, inspectable output."""
import json
import tempfile
import unittest
from pathlib import Path

from cloudops_lab.replay import run_replay


class ReplayTests(unittest.TestCase):
    def test_replay_generates_four_valid_incidents(self) -> None:
        with tempfile.TemporaryDirectory() as location:
            result = run_replay(Path(location))
            self.assertTrue(result['complete'])
            self.assertEqual(result['successful_scenarios'], 4)
            self.assertTrue(all(s['recovery_verified'] for s in result['scenarios']))
            json_file = Path(location) / 'incident-replay.json'
            markdown_file = Path(location) / 'incident-replay.md'
            self.assertTrue(json_file.is_file())
            self.assertTrue(markdown_file.is_file())
            self.assertEqual(json.loads(json_file.read_text())['total_scenarios'], 4)
            self.assertIn('synthetic local environment', markdown_file.read_text())

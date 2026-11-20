import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cloudops_lab.cli import _write_control, main


class CliTests(unittest.TestCase):
    def test_control_file_private_and_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'control.json'
            _write_control(output, {'token': 'example'})
            self.assertEqual(json.loads(output.read_text())['token'], 'example')
            if os.name == 'posix':
                self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)

    def test_invalid_control_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {'CLOUDOPS_CONTROL_FILE': str(Path(directory) / 'missing.json')}):
                self.assertEqual(main(['status']), 2)

    def test_invalid_server_bind_rejected(self) -> None:
        self.assertEqual(main(['serve', '--bind', '192.168.0.1']), 2)
        self.assertEqual(main(['serve', '--bind', '0.0.0.0']), 2)

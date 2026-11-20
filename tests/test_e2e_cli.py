"""Black-box exercise of the command-line engineering workflow."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


class EndToEndCliTests(unittest.TestCase):
    def test_start_inject_probe_and_recover(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            control_file = Path(temp) / 'control.json'
            environment = dict(os.environ, CLOUDOPS_CONTROL_FILE=str(control_file))
            process = subprocess.Popen([sys.executable, '-m', 'cloudops_lab', 'serve', '--port', '0'],
                                       env=environment, stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
            try:
                for _ in range(50):
                    if control_file.exists():
                        break
                    if process.poll() is not None:
                        self.fail('Lab server exited unexpectedly')
                    time.sleep(0.05)
                self.assertTrue(control_file.exists())
                control = json.loads(control_file.read_text())
                self.assertTrue(control['url'].startswith('http://127.0.0.1:'))

                def cli(*arguments: str) -> subprocess.CompletedProcess[str]:
                    return subprocess.run([sys.executable, '-m', 'cloudops_lab', *arguments],
                                          env=environment, capture_output=True, text=True, timeout=5)

                self.assertEqual(cli('status').returncode, 0)
                self.assertEqual(cli('probe', '--requests', '1').returncode, 0)
                self.assertEqual(cli('inject', 'dependency_outage').returncode, 0)
                unhealthy = cli('status')
                self.assertEqual(unhealthy.returncode, 0)
                self.assertIn('"readiness_http": 503', unhealthy.stdout)
                self.assertEqual(cli('probe', '--requests', '1').returncode, 1)
                self.assertEqual(cli('recover').returncode, 0)
                self.assertEqual(cli('probe', '--requests', '1').returncode, 0)
            finally:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)

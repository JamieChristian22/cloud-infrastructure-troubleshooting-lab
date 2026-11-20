"""Read-only host and single-endpoint troubleshooting checks. No port scanning."""
import json
import os
import platform
import shutil
import socket
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import Any


def linux_snapshot(path: str = '.') -> dict[str, Any]:
    disk = shutil.disk_usage(path)
    memory: dict[str, int] = {}
    if platform.system() == 'Linux' and Path('/proc/meminfo').exists():
        for line in Path('/proc/meminfo').read_text().splitlines():
            key, _, value = line.partition(':')
            if key in {'MemTotal', 'MemAvailable', 'SwapTotal', 'SwapFree'}:
                memory[key + '_kib'] = int(value.strip().split()[0])
    return {'collected_at_utc': datetime.now(timezone.utc).isoformat(),
            'platform': platform.system(), 'os_release': platform.release(),
            'cpu_count': os.cpu_count(), 'disk': {'path': str(Path(path).resolve()),
            'total_bytes': disk.total, 'free_bytes': disk.free,
            'free_percent': round(disk.free / disk.total * 100, 2) if disk.total else 0},
            'memory': memory, 'scope': 'local host, read-only'}


def network_snapshot(host: str = 'localhost', port: int = 8080, timeout: float = 1.5) -> dict[str, Any]:
    result: dict[str, Any] = {'host': host, 'port': port, 'dns_resolved': False,
                               'tcp_connected': False, 'scope': 'single host and port'}
    start = monotonic()
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        result['addresses'] = sorted({str(item[4][0]) for item in infos})
        result['dns_resolved'] = True
    except OSError as exc:
        result['diagnosis'] = f'DNS lookup failed: {type(exc).__name__}'
        return result
    try:
        with socket.create_connection((host, port), timeout=timeout):
            result['tcp_connected'] = True
    except OSError as exc:
        result['diagnosis'] = f'TCP connection failed: {type(exc).__name__}'
    result['elapsed_ms'] = round((monotonic() - start) * 1000, 2)
    if result['tcp_connected']:
        result['diagnosis'] = 'TCP connectivity OK; check HTTP readiness and application logs next'
    return result


def as_json(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True)

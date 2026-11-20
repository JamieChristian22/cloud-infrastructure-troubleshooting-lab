"""Operational CLI for safe failure injection and diagnosis on a local service."""
import argparse
import json
import logging
import os
import secrets
import sys
from pathlib import Path
from typing import Any

from .client import request
from .replay import run_replay
from .server import build_server
from .state import FAULTS
from .triage import as_json, linux_snapshot, network_snapshot


def control_path() -> Path:
    return Path(os.environ.get('CLOUDOPS_CONTROL_FILE', '.lab/control.json'))


def _write_control(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # 0600 prevents another local user from reading the control token by default.
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as file:
            json.dump(data, file)
            file.write('\n')
    except Exception:
        path.unlink(missing_ok=True)
        raise
    os.chmod(path, 0o600)


def _control() -> dict[str, Any]:
    path = control_path()
    if not path.exists():
        raise RuntimeError(f'No running lab control file at {path}. Start `python -m cloudops_lab serve`.')
    return json.loads(path.read_text(encoding='utf-8'))


def _run(args: argparse.Namespace) -> int:
    if args.command == 'serve':
        if args.bind not in ('127.0.0.1', 'localhost', '::1', '0.0.0.0'):
            raise ValueError('Supported bind addresses: 127.0.0.1, localhost, ::1, 0.0.0.0')
        if args.bind == '0.0.0.0' and not args.allow_non_loopback:
            raise ValueError('Exposing the lab to a network requires --allow-non-loopback and access controls.')
        token = secrets.token_urlsafe(32)
        server = build_server(args.bind, args.port, token=token)
        local_url = f'http://127.0.0.1:{server.server_port}'
        _write_control(control_path(), {'url': local_url, 'token': token, 'pid': os.getpid()})
        logging.basicConfig(format='%(message)s', level=logging.INFO)
        print(f'Local incident lab listening on port {server.server_port}', flush=True)
        print('Control token saved with 0600 permissions; never commit .lab/control.json', flush=True)
        try:
            server.serve_forever()
        finally:
            server.server_close()
            path = control_path()
            if path.exists():
                try:
                    if json.loads(path.read_text()).get('token') == token:
                        path.unlink()
                except (ValueError, OSError):
                    pass
        return 0
    if args.command == 'demo':
        report = run_replay(Path(args.output))
        print(f"Scenarios passed: {report['successful_scenarios']}/{report['total_scenarios']}")
        print(f'Evidence: {args.output}/incident-replay.json and .md')
        return 0 if report['complete'] else 1
    if args.command == 'linux':
        print(as_json(linux_snapshot(args.path)))
        return 0
    if args.command == 'network':
        print(as_json(network_snapshot(args.host, args.port)))
        return 0
    control = _control()
    base_url, token = control['url'], control['token']
    if args.command in {'inject', 'recover'}:
        fault = args.fault if args.command == 'inject' else 'none'
        status, value = request(base_url, '/ops/fault', token=token, body={'fault': fault})
        print(as_json({'http_status': status, 'response': value}))
        return 0 if status == 200 else 1
    if args.command == 'status':
        live, _ = request(base_url, '/health/live')
        ready, _ = request(base_url, '/health/ready')
        auth, state = request(base_url, '/ops/state', token=token)
        print(as_json({'liveness_http': live, 'readiness_http': ready, 'runtime': state}))
        return 0 if auth == 200 else 1
    if args.command == 'probe':
        observations = []
        for _ in range(args.requests):
            try:
                code, response = request(base_url, '/api/orders', timeout=5)
                observations.append({'http_status': code, 'response': response})
            except OSError as exc:
                observations.append({'error': type(exc).__name__})
        print(as_json({'observations': observations,
                       'success_count': sum(x.get('http_status') == 200 for x in observations)}))
        return 0 if all(x.get('http_status') == 200 for x in observations) else 1
    raise ValueError(f'Unsupported command {args.command}')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='cloudops-lab', description='Offline-first cloud reliability and troubleshooting lab')
    sub = parser.add_subparsers(dest='command', required=True)
    server = sub.add_parser('serve', help='Start the local API, metrics, and failure simulator')
    server.add_argument('--bind', default='127.0.0.1')
    server.add_argument('--port', default=8080, type=int)
    server.add_argument('--allow-non-loopback', action='store_true')
    sub.add_parser('status', help='Inspect liveness, readiness, and active fault')
    inject = sub.add_parser('inject', help='Enable a simulated production failure')
    inject.add_argument('fault', choices=[item for item in FAULTS if item != 'none'])
    sub.add_parser('recover', help='Clear a failure and restore service health')
    probe = sub.add_parser('probe', help='Probe the simulated order API')
    probe.add_argument('--requests', default=3, type=int, choices=range(1, 21), metavar='1..20')
    demo = sub.add_parser('demo', help='Execute and capture all four supported fault scenarios')
    demo.add_argument('--output', default='evidence')
    linux = sub.add_parser('linux', help='Capture read-only local system diagnostics')
    linux.add_argument('--path', default='.')
    network = sub.add_parser('network', help='Inspect DNS resolution and one TCP destination')
    network.add_argument('--host', default='localhost')
    network.add_argument('--port', type=int, default=8080)
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except (RuntimeError, ValueError, ConnectionError, OSError, json.JSONDecodeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2

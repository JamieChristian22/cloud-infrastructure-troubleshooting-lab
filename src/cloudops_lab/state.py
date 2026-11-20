"""Thread-safe in-memory state for a deliberately local incident-response lab."""
from collections import Counter, deque
from threading import RLock
from time import monotonic
from typing import Any

FAULTS = ('none', 'dependency_outage', 'high_latency', 'application_error', 'auth_misconfig')


class RuntimeState:
    def __init__(self) -> None:
        self._lock = RLock()
        self._started = monotonic()
        self._fault = 'none'
        self._requests: Counter[tuple[str, int]] = Counter()
        self._durations: Counter[str] = Counter()
        self._duration_sum: dict[str, float] = {}
        self._events: deque[dict[str, Any]] = deque(maxlen=100)

    def set_fault(self, value: str) -> None:
        if value not in FAULTS:
            raise ValueError(f'Unknown fault: {value}')
        with self._lock:
            self._fault = value

    @property
    def fault(self) -> str:
        with self._lock:
            return self._fault

    def record(self, route: str, status: int, seconds: float) -> None:
        with self._lock:
            self._requests[(route, status)] += 1
            self._durations[route] += 1
            self._duration_sum[route] = self._duration_sum.get(route, 0.0) + seconds
            self._events.append({'route': route, 'status': status, 'duration_ms': round(seconds * 1000, 2)})

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            codes: Counter[str] = Counter()
            for (_, status), number in self._requests.items():
                codes[str(status)] += number
            return {
                'fault': self._fault,
                'uptime_seconds': round(monotonic() - self._started, 2),
                'requests_total': sum(self._requests.values()),
                'status_counts': dict(sorted(codes.items())),
                'recent_events': list(self._events)[-15:],
            }

    def prometheus(self) -> str:
        with self._lock:
            out = ['# HELP lab_requests_total Number of HTTP requests by route and status.',
                   '# TYPE lab_requests_total counter']
            for (route, status), number in sorted(self._requests.items()):
                out.append(f'lab_requests_total{{route="{route}",status="{status}"}} {number}')
            out += ['# HELP lab_request_duration_seconds_sum Total elapsed request time.',
                    '# TYPE lab_request_duration_seconds_sum counter']
            for route, total in sorted(self._duration_sum.items()):
                out.append(f'lab_request_duration_seconds_sum{{route="{route}"}} {total:.6f}')
            out += ['# HELP lab_request_duration_seconds_count Total observed requests.',
                    '# TYPE lab_request_duration_seconds_count counter']
            for route, number in sorted(self._durations.items()):
                out.append(f'lab_request_duration_seconds_count{{route="{route}"}} {number}')
            out += ['# HELP lab_fault_active Whether any simulated fault is active.',
                    '# TYPE lab_fault_active gauge',
                    f'lab_fault_active {0 if self._fault == "none" else 1}',
                    '# HELP lab_uptime_seconds Time since lab server start.',
                    '# TYPE lab_uptime_seconds gauge',
                    f'lab_uptime_seconds {monotonic() - self._started:.3f}']
            return '\n'.join(out) + '\n'

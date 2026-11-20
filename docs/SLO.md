# Local reliability objectives and proposed SLOs

**Scope:** Educational, synthetic local API. These are **proposed** targets and not measured production SLAs. No real users, uptime commitments or cloud charges are involved.

## Service-level indicators (SLIs)

- **Availability:** Share of `/api/orders` requests returning HTTP status other than 5xx. Authentication failure (401) is tracked separately and is not counted as an availability error unless an agreed service policy says otherwise.
- **Latency:** p95 of `/api/orders` request duration, from `lab_request_duration_histogram_seconds_bucket`.
- **Readiness:** `/health/ready` is a separate diagnostic check, not a substitute for the business endpoint.

## Proposed goals (not yet established using long-term traffic)

| Objective | Example target | Example evaluation period |
| --- | --- | --- |
| Availability | 99.5% | 28 rolling days |
| API p95 latency | 250 milliseconds | 28 rolling days |
| Recovery procedure | Show a 200 response after each controlled incident | Every fault replay |

Synthetic, manually injected failures intentionally violate these goals. A 28-day SLO cannot be honestly computed from a short demo.

## Prometheus queries

5xx fraction of API requests over 5 minutes:

```promql
sum(rate(lab_requests_total{route="/api/orders",status=~"5.."}[5m]))
/
clamp_min(sum(rate(lab_requests_total{route="/api/orders"}[5m])), 0.000001)
```

p95 API latency over 5 minutes:

```promql
histogram_quantile(
  0.95,
  sum by (le) (rate(lab_request_duration_histogram_seconds_bucket{route="/api/orders"}[5m]))
)
```

**Limitations:** Histograms are coarse buckets, the metrics are in-memory, short windows can be noisy, and no external traffic generator or 28-day environment is configured. A missing series is **not** evidence of 100% uptime.

## Optional monitoring stack

From the repository root:

```bash
export GRAFANA_ADMIN_PASSWORD='choose-your-own-local-password'
docker compose -f compose.yaml -f compose.monitoring.yaml up -d --build
```

Open [Grafana on localhost](http://127.0.0.1:3000) and [Prometheus on localhost](http://127.0.0.1:9090). Use the `CloudOps Lab — Service Reliability` dashboard under the `CloudOps Lab` folder. Run `python -m cloudops_lab demo` or send requests to populate telemetry; without traffic some time-series panels show no data.

```bash
docker compose -f compose.yaml -f compose.monitoring.yaml down --volumes
```

Only expose ports on loopback; Grafana does not use anonymous access, and you must set an admin password. The monitoring stack is local and intentionally ephemeral; stopping and removing containers may discard historical telemetry. Docker validation and live monitoring checks are separately recorded in [verification](verification.md).

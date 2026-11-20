# Architecture and engineering decisions

## Problem statement

A junior cloud or application engineer needs repeatable evidence of troubleshooting a service that can appear healthy while downstream operations fail. This local lab supports fault injection, time correlation, recovery verification, and inspectable evidence without a cloud account.

## Logical topology

```mermaid
sequenceDiagram
  actor Engineer
  participant CLI
  participant API as Python HTTP Service
  participant Runtime as In-memory Fault State
  participant Evidence as Report Files
  Engineer->>CLI: demo / inject / probe
  CLI->>API: GET /health/ready
  API->>Runtime: read active fault
  API-->>CLI: 200 ready or 503 not ready
  CLI->>API: POST /ops/fault (token)
  API->>Runtime: set fault
  CLI->>API: GET /api/orders
  API-->>CLI: 200 / 401 / 500 / 503
  CLI->>API: POST /ops/fault (none)
  CLI->>API: GET /api/orders
  API-->>CLI: 200 recovered
  CLI->>Evidence: Write JSON and Markdown
```

## Operational signals

| Signal | Collection | Interpretation | Limitation |
| --- | --- | --- | --- |
| Liveness | `GET /health/live` | Process and handler reachable | Not proof upstream data is available |
| Readiness | `GET /health/ready` | Local SQLite can execute a query | In-memory test data, not external database availability |
| Error rate | `lab_requests_total` by status | Determine what fraction fails | Process-local; resets on restart |
| Latency | `lab_request_duration_histogram_seconds_bucket` and sum/count | p95 estimates and mean latency | Coarse histogram buckets, no long-running SLO proof |
| Fault state | `lab_fault_active` | Incident currently injected | Lab simulation only |
| HTTP request IDs | `X-Request-ID` + JSON event logs | Support correlation | Not distributed tracing |

## Failure taxonomy

1. **503 dependency unavailable:** close the real in-memory SQLite connection; liveness stays healthy, readiness becomes unhealthy, and the order API returns 503. Recovery reopens and reseeds the local database.
2. **Slow but 200:** readiness healthy but response times regress, so errors alone will miss the incident.
3. **500 application failure:** a request path breaks while health checks continue serving.
4. **401 authentication misconfiguration:** a simulated upstream identity failure, not an authentication bypass.

## Fault-control boundaries

- Default bind: `127.0.0.1`; non-loopback binding requires explicit opt-in.
- `/ops/fault` and `/ops/state` require a randomly generated token.
- Local token file uses mode `0600`; `.lab/` is gitignored.
- Faults exist only in memory and clear on restart.
- Metrics use fixed low-cardinality route labels; query parameters aren't logged.
- This server is not internet-facing production software: it has no TLS, durable metrics backend, or rate limiting.

## Implementation scope

**Verified:** Python service and CLI, local replay and tests; GitHub Actions verifies Python versions and a Docker build, health check, database outage and recovery. Check the current Actions results for the monitoring run.

**Optional local monitoring:** Prometheus scrapes the API from the Compose network; a pre-provisioned Grafana dashboard charts injected faults, API error ratios, rates and p95 latency. Runtime verification depends on the monitoring CI job.

**Not implemented:** AWS provisioning, Terraform deployment, Kubernetes, durable storage, external alerting, distributed tracing, cloud billing telemetry, genuine upstream authentication, or production-grade security controls.

## Next engineering steps

Add measured sustained load tests, bounded retries and timeouts with unit tests, dependable alert routing, and evidence-backed deployment/rollback. See [SLO plan](SLO.md).

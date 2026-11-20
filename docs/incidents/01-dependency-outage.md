# Incident 01 — Readiness failed while process stayed alive

**Environment:** Synthetic local lab, NOT a production or customer incident.
**Evidence source:** [Original executed replay](../../evidence/incident-replay.json), generated 2026-11-20 00:34:49 UTC under the original status-only simulator. Newer code adds a real local SQLite connection for the dependency scenario. CI replays provide newer artifacts.

## Initial signal and impact

Baseline before fault injection: readiness **200**, sample order API **200**. After injecting `dependency_outage`:

| Evidence | Observed |
| --- | --- |
| Readiness HTTP | 503 |
| Orders API HTTP | 503 |
| Orders API latency in the original replay | 0.59 ms |
| Recovery API HTTP after clearing fault | 200 |
| Test result | PASS |

**Scope:** One fictional order API and injected local failure. No actual customer or external cloud impact.

## Investigation and diagnosis

A 503 on readiness plus 503 on the order route indicates a dependency issue rather than a dead process. The liveness endpoint remains reachable by design. In the **upgraded** implementation, fault injection closes a real local SQLite connection; the API's readiness query fails until reconnect.

**Confirmed cause:** The operator intentionally selected the `dependency_outage` fault. The evidence verifies observable behavior, not an organically discovered production root cause. `dependency_unavailable` is the synthetic response indication.

## Containment and verified recovery

1. Inspect `python -m cloudops_lab status` for readiness and active fault.
2. Probe `/api/orders` and correlate returned status with metrics and structured request IDs.
3. Clear the injected fault using `python -m cloudops_lab recover`.
4. Verify `/health/ready` and the business API; the saved replay records an API HTTP **200** after recovery.
5. Record any remaining limitations before closing the investigation.

## Operational learning and next safeguard

Do not equate a liveness 200 with a healthy business transaction. Correlate readiness and the failing API before changing infrastructure.

**Prevention / follow-up:** Retain a dedicated dependency integration test and confirm both query failure and recovery. No RDS or external database was used.

See the [repeatable runbook](../runbooks/01-dependency-outage.md), the [SLO plan](../SLO.md), and the timestamped [JSON artifact](../../evidence/incident-replay.json).

## Evidence honesty

This document is a **case study of the scripted exercise**, not a real-world incident postmortem. Durations are original replay samples, not SLA data. In particular, the original dependency replay preceded the SQLite implementation, and should not be used as evidence that the initial run closed a database connection.

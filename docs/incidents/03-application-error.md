# Incident 03 — Order route failed while health stayed ready

**Environment:** Synthetic local lab, NOT a production or customer incident.
**Evidence source:** [Original executed replay](../../evidence/incident-replay.json), generated 2026-11-20 00:34:49 UTC under the original status-only simulator. Newer code adds a real local SQLite connection for the dependency scenario. CI replays provide newer artifacts.

## Initial signal and impact

Baseline before fault injection: readiness **200**, sample order API **200**. After injecting `application_error`:

| Evidence | Observed |
| --- | --- |
| Readiness HTTP | 200 |
| Orders API HTTP | 500 |
| Orders API latency in the original replay | 0.69 ms |
| Recovery API HTTP after clearing fault | 200 |
| Test result | PASS |

**Scope:** One fictional order API and injected local failure. No actual customer or external cloud impact.

## Investigation and diagnosis

Readiness 200 with an order route HTTP 500 points toward a request-path fault rather than a general process outage. In real operations, inspect exception logs, deploy history and traces; the synthetic test intentionally returns a 500 rather than raising an unexpected server crash.

**Confirmed cause:** The operator intentionally selected the `application_error` fault. The evidence verifies observable behavior, not an organically discovered production root cause. `application_failure` is the synthetic response indication.

## Containment and verified recovery

1. Inspect `python -m cloudops_lab status` for readiness and active fault.
2. Probe `/api/orders` and correlate returned status with metrics and structured request IDs.
3. Clear the injected fault using `python -m cloudops_lab recover`.
4. Verify `/health/ready` and the business API; the saved replay records an API HTTP **200** after recovery.
5. Record any remaining limitations before closing the investigation.

## Operational learning and next safeguard

Avoid closing the incident based on a green readiness endpoint alone; test the affected business route after mitigation.

**Prevention / follow-up:** Keep an API contract regression test, structured request IDs and route-specific error counts.

See the [repeatable runbook](../runbooks/03-application-error.md), the [SLO plan](../SLO.md), and the timestamped [JSON artifact](../../evidence/incident-replay.json).

## Evidence honesty

This document is a **case study of the scripted exercise**, not a real-world incident postmortem. Durations are original replay samples, not SLA data. In particular, the original dependency replay preceded the SQLite implementation, and should not be used as evidence that the initial run closed a database connection.

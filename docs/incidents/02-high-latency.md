# Incident 02 — Order API was slow but still returned 200

**Environment:** Synthetic local lab, NOT a production or customer incident.
**Evidence source:** [Original executed replay](../../evidence/incident-replay.json), generated 2026-11-20 00:34:49 UTC under the original status-only simulator. Newer code adds a real local SQLite connection for the dependency scenario. CI replays provide newer artifacts.

## Initial signal and impact

Baseline before fault injection: readiness **200**, sample order API **200**. After injecting `high_latency`:

| Evidence | Observed |
| --- | --- |
| Readiness HTTP | 200 |
| Orders API HTTP | 200 |
| Orders API latency in the original replay | 301 ms |
| Recovery API HTTP after clearing fault | 200 |
| Test result | PASS |

**Scope:** One fictional order API and injected local failure. No actual customer or external cloud impact.

## Investigation and diagnosis

A valid HTTP 200 hid approximately 301ms of injected delay. Error counters would not detect this fault alone. Query duration histograms and estimate p95 over a meaningful interval; note that one sample is insufficient for an SLO conclusion.

**Confirmed cause:** The operator intentionally selected the `high_latency` fault. The evidence verifies observable behavior, not an organically discovered production root cause. `data_classification: synthetic` is the synthetic response indication.

## Containment and verified recovery

1. Inspect `python -m cloudops_lab status` for readiness and active fault.
2. Probe `/api/orders` and correlate returned status with metrics and structured request IDs.
3. Clear the injected fault using `python -m cloudops_lab recover`.
4. Verify `/health/ready` and the business API; the saved replay records an API HTTP **200** after recovery.
5. Record any remaining limitations before closing the investigation.

## Operational learning and next safeguard

Monitor latency separately from success rate, and compare slow paths against baseline and dependency signals.

**Prevention / follow-up:** Use histogram-based queries, load tests and a clear p95 target. Do not claim a production latency improvement from the injected result.

See the [repeatable runbook](../runbooks/02-high-latency.md), the [SLO plan](../SLO.md), and the timestamped [JSON artifact](../../evidence/incident-replay.json).

## Evidence honesty

This document is a **case study of the scripted exercise**, not a real-world incident postmortem. Durations are original replay samples, not SLA data. In particular, the original dependency replay preceded the SQLite implementation, and should not be used as evidence that the initial run closed a database connection.

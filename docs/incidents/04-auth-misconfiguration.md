# Incident 04 — Simulated upstream authentication rejected

**Environment:** Synthetic local lab, NOT a production or customer incident.
**Evidence source:** [Original executed replay](../../evidence/incident-replay.json), generated 2026-11-20 00:34:49 UTC under the original status-only simulator. Newer code adds a real local SQLite connection for the dependency scenario. CI replays provide newer artifacts.

## Initial signal and impact

Baseline before fault injection: readiness **200**, sample order API **200**. After injecting `auth_misconfig`:

| Evidence | Observed |
| --- | --- |
| Readiness HTTP | 200 |
| Orders API HTTP | 401 |
| Orders API latency in the original replay | 0.66 ms |
| Recovery API HTTP after clearing fault | 200 |
| Test result | PASS |

**Scope:** One fictional order API and injected local failure. No actual customer or external cloud impact.

## Investigation and diagnosis

HTTP 401 with normal readiness suggests an identity/configuration issue rather than a TCP failure. In a real system, distinguish the source of 401 and review service identity, scope, audience and expiry without exposing tokens. The original lab did not communicate with a genuine identity provider.

**Confirmed cause:** The operator intentionally selected the `auth_misconfig` fault. The evidence verifies observable behavior, not an organically discovered production root cause. `upstream_authentication_failed` is the synthetic response indication.

## Containment and verified recovery

1. Inspect `python -m cloudops_lab status` for readiness and active fault.
2. Probe `/api/orders` and correlate returned status with metrics and structured request IDs.
3. Clear the injected fault using `python -m cloudops_lab recover`.
4. Verify `/health/ready` and the business API; the saved replay records an API HTTP **200** after recovery.
5. Record any remaining limitations before closing the investigation.

## Operational learning and next safeguard

Classify 401 separately from 5xx availability errors, and do not rotate production credentials based on a synthetic event.

**Prevention / follow-up:** Document secure credential rotation, secrets redaction, authorization regression tests and escalation boundaries.

See the [repeatable runbook](../runbooks/04-auth-misconfig.md), the [SLO plan](../SLO.md), and the timestamped [JSON artifact](../../evidence/incident-replay.json).

## Evidence honesty

This document is a **case study of the scripted exercise**, not a real-world incident postmortem. Durations are original replay samples, not SLA data. In particular, the original dependency replay preceded the SQLite implementation, and should not be used as evidence that the initial run closed a database connection.

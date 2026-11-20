# Runbook 01 — Dependency outage and readiness failure

**Career focus:** Cloud Support / Application Support · **Environment:** local simulation

## Objective

Distinguish a reachable process from an application that is ready to serve requests. Isolate the dependency failure and verify actual API recovery.

## Reproduce

Start the service in a second terminal, then run:

```bash
python -m cloudops_lab status
python -m cloudops_lab inject dependency_outage
python -m cloudops_lab status
python -m cloudops_lab probe --requests 3
curl -i http://127.0.0.1:8080/health/live
curl -i http://127.0.0.1:8080/health/ready
```

**Expected:** liveness 200, readiness 503, order API 503. The probe exits nonzero during the injected incident; this is expected.

## Troubleshooting sequence

1. Check whether liveness and readiness disagree.
2. Compare failure statuses and request counts via `/metrics`.
3. In a real environment, review dependency health, DNS/TCP, configuration, timeouts, and recent deploys.
4. In this lab, confirm the deliberate fault using `status`; there is no real upstream service to repair.

## Recovery

```bash
python -m cloudops_lab recover
python -m cloudops_lab status
python -m cloudops_lab probe --requests 3
```

**Done when:** readiness and the order API return 200. Record the simulated root cause using the [incident template](../incident-report-template.md).

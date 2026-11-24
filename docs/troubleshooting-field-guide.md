# Cloud Support Troubleshooting Field Guide

A free, reusable practice resource for junior cloud engineers, technical support engineers and anyone learning incident investigation. No cloud account, paid software, or AWS deployment is required. The exercises use this repository's fictional local order service.

## Start with a question, not a fix

1. What is failing, for whom, and since when?
2. Can I reproduce it safely?
3. Is the process alive? Is it ready? Does the actual request work?
4. Which layer has evidence of failure: DNS, TCP, HTTP, application or dependency?
5. What single reversible change is justified?
6. Can I prove recovery with the same request and document what remains uncertain?

## A 20-minute local practice session

Use Python 3.11+ and a dedicated virtual environment. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux; on Windows use the appropriate activation script
python -m pip install -e .
python -m cloudops_lab serve
```

In a second terminal with the same virtual environment active, establish a healthy baseline:

```bash
python -m cloudops_lab status
curl -i http://127.0.0.1:8080/health/live
curl -i http://127.0.0.1:8080/health/ready
curl -i http://127.0.0.1:8080/api/orders
```

If another service already uses port 8080, stop and consult the project README. Do not stop an unfamiliar service.

In this **local lab only**, introduce a dependency fault:

```bash
python -m cloudops_lab inject dependency_outage
python -m cloudops_lab status
curl -i http://127.0.0.1:8080/health/live
curl -i http://127.0.0.1:8080/health/ready
curl -i http://127.0.0.1:8080/api/orders
```

Expected signals: liveness stays healthy, readiness and the orders endpoint return HTTP 503. In the current implementation, the lab disconnects a local SQLite dependency. Record actual results; don't substitute expectations for observations.

Restore the lab and repeat the checks:

```bash
python -m cloudops_lab recover
python -m cloudops_lab status
curl -i http://127.0.0.1:8080/health/ready
curl -i http://127.0.0.1:8080/api/orders
```

Expected recovery: readiness and the orders API return 200. Stop your own server with Ctrl+C in the first terminal when finished.

## Diagnostic decision table

| Observed signal | What it suggests | Next safe observation |
| --- | --- | --- |
| Hostname fails to resolve | DNS or local name resolution issue | Confirm hostname and resolver configuration; do not assume service outage |
| TCP connection refused | No accepting listener, explicit rejection or another connectivity issue | Check local listener and service state |
| TCP times out | Possible network path, firewall or unresponsive destination | Confirm target and review authorized network evidence |
| Live 200, ready 503, orders 503 | A process is alive but unable to serve the request | Inspect dependency status and application logs |
| Ready 200, orders 500 | Health checks do not cover the failed application path | Correlate request IDs, logs and recent changes |
| Orders 401 | Authentication failed or upstream auth is misconfigured | Check credential configuration and scope without printing secrets |
| Orders 200 but slow | Successful HTTP status alone does not guarantee acceptable latency | Compare repeated timings to a healthy baseline |

These are hypotheses, not guaranteed root causes. Use read-only observations first; never run fault injection, restart services or modify infrastructure you do not own or have authorization to operate.

## Reusable incident worksheet

Copy these fields into your own notes (do not commit secrets or real customer data).

| Field | Your observation |
| --- | --- |
| Incident ID and UTC time | |
| Environment and affected endpoint | |
| Expected behavior and actual behavior | |
| Scope and severity rationale | |
| Baseline and failing signals | |
| Two competing hypotheses | |
| Evidence that supports or rules out each | |
| Authorized recovery action | |
| Post-recovery verification | |
| Remaining uncertainties and next steps | |

## Evidence and collaboration

- [Incident replay](../evidence/incident-replay.md) — historical synthetic replay; see [verification record](verification.md) for the later SQLite implementation and testing scope.
- [Dependency outage runbook](runbooks/01-dependency-outage.md) — more investigation detail.
- [Contributing](../CONTRIBUTING.md) — suggest a reproducible correction or learning exercise, if issues are enabled.

This guide is a newly authored learning resource, not a record of an additional completed lab run. Current CI results and live cloud behavior must be verified separately. Share it with someone learning cloud support, or offer constructive feedback. Sponsorship is entirely optional: https://github.com/sponsors/JamieChristian22.

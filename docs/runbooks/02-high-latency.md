# Runbook 02 — Slow response despite HTTP 200

**Career focus:** SRE / Application Performance / Observability · **Environment:** local simulation

## Objective

Diagnose degraded latency even though the API continues returning success.

```bash
python -m cloudops_lab probe --requests 3
python -m cloudops_lab inject high_latency
python -m cloudops_lab probe --requests 3
curl -s http://127.0.0.1:8080/metrics
python -m cloudops_lab recover
python -m cloudops_lab probe --requests 3
```

**Expected:** orders still return HTTP 200, but with an intentional ~300ms delay. Observe `lab_request_duration_seconds_sum` and `_count`.

**Reasoning:** Check upstream latency, database queries, resource saturation, trace timing, and recent releases before making changes in an actual service. This lab uses a deterministic sleep; it is not a real CPU or cloud bottleneck.

**Recovery:** compare response times before and after clearing the fault. This lab does not yet provide percentile histograms or a validated production SLO.

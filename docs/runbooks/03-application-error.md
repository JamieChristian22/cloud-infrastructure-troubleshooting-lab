# Runbook 03 — HTTP 500 failure

**Career focus:** API Troubleshooting / Incident Response / Logging · **Environment:** local simulation

```bash
python -m cloudops_lab inject application_error
python -m cloudops_lab status
python -m cloudops_lab probe --requests 2
curl -i http://127.0.0.1:8080/api/orders
curl -s http://127.0.0.1:8080/metrics
```

**Expected:** orders return HTTP 500 while health handlers remain reachable. The response is deliberately injected, not an unhandled Python exception.

**Investigation:** correlate request ID, structured JSON logs, and error counts. On a real service inspect application exceptions, query failures, serialization, deployment changes, and dependency status without logging credentials.

```bash
python -m cloudops_lab recover
python -m cloudops_lab probe --requests 2
```

**Done when:** the previously failing API returns HTTP 200. Document simulation limitations.

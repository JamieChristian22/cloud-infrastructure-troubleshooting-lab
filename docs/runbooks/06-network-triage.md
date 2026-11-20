# Runbook 06 — DNS, TCP, and HTTP fault isolation

**Career focus:** Networking / Cloud Support / Application Support · **Mode:** single-target read-only probe

Start the server before running:

```bash
python -m cloudops_lab network --host localhost --port 8080
python -m cloudops_lab network --host localhost --port 9
curl -i http://127.0.0.1:8080/health/ready
```

The command resolves one hostname and tests one TCP port. A completed TCP connection does not imply the application is healthy. Port 9 is typically closed but that is not guaranteed.

| Symptom | Next investigation |
| --- | --- |
| DNS fails | DNS configuration, hostname, split-horizon |
| DNS works, TCP fails | Listener, route, firewall/security group, service state |
| TCP works, HTTP 503 | Application/dependency readiness |
| HTTP 200, slow | Resource pressure, upstream timing, latency metrics |

**Safety:** This is not a port scanner. Check only systems you own or are authorized to test; no network settings are modified.

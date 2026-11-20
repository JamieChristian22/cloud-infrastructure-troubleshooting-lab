# Runbook 04 — Upstream authentication misconfiguration

**Career focus:** IAM / Cloud Support / API Diagnosis · **Environment:** local simulation

```bash
python -m cloudops_lab inject auth_misconfig
python -m cloudops_lab probe --requests 2
python -m cloudops_lab status
```

**Expected:** orders return 401 because the simulated upstream identity is invalid. This is not a bypass of real authentication.

**Production investigation:** identify which layer returns 401; check service identity, token expiry, scopes/audience, secrets rotation, and configuration without exposing token values. Separate authentication errors from network faults.

```bash
python -m cloudops_lab recover
python -m cloudops_lab probe --requests 2
```

**Done when:** orders return 200 and the incident report makes clear this was a mock misconfiguration.

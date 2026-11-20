# Runbook 05 — Linux host diagnostics

**Career focus:** Linux / Cloud Support / Systems Engineering · **Mode:** real local read-only inspection

```bash
python -m cloudops_lab linux
```

Python gathers disk capacity, OS/kernel, CPU count, and Linux `/proc/meminfo` values where available. No root privileges or system changes are needed.

**Interpretation:** insufficient free disk space can prevent deployments and logs from writing; low memory may indicate resource pressure. A snapshot alone is not a verified root cause.

## Manual Linux command practice

```bash
uname -a
df -h
free -h
ps aux
systemctl --failed
journalctl -p err -n 30 --no-pager
```

These commands are study examples, not automatically executed by the project. Never run diagnostics on systems without authorization; availability and permissions vary by OS.

# Verification record and evidence policy

## Executed locally during initial build

| Verification | Method | Result |
| --- | --- | --- |
| Python installation | `python -m pip install -e . --no-build-isolation` | Successful in initial environment |
| Automated tests | `python -m unittest discover -s tests -v` | 19 tests passed |
| Full outage replay | `python -m cloudops_lab demo --output evidence` | 4 scenarios passed and recovered |
| Linux diagnostics | `python -m cloudops_lab linux` | Local JSON snapshot generated |
| DNS and TCP check | `python -m cloudops_lab network --host localhost --port 9` | Local hostname resolved; unused port refused |

Reproduction artifacts are stored in [evidence](../evidence/). Timestamps and latencies change between runs. Synthetic tests do not prove real cloud network behavior.

## GitHub Actions verified on upgrade branch

- The first upgrade run passed Python 3.11/3.12/3.13 verification, dependency integration tests and a Docker/Compose real SQLite disconnect-and-recover smoke test on November 20, 2026 UTC. [Inspect the passing workflow](https://github.com/JamieChristian22/cloud-infrastructure-troubleshooting-lab/actions/runs/44655835722).
- The optional monitoring overlay has its own CI smoke job in the expanded workflow. Verify its actual completion and artifacts in [Actions](https://github.com/JamieChristian22/cloud-infrastructure-troubleshooting-lab/actions); adding files is not evidence that a dashboard runs.
- The retained replay JSON/Markdown at `evidence/` was generated **before** SQLite was added, from a synthetic status-only fault. CI produces new per-run evidence against the upgraded SQLite implementation.

## Not independently verified by the initial build

- Docker runtime on the recruiter's personal workstation (CI Docker verification exists).
- Long-running dashboard and monitoring behavior outside CI.
- Terraform or AWS deployment and billing (not part of this version).
- Substantial-load benchmarks, production SLOs, and internet-exposed security review.

## Evidence authenticity

1. Distinguish automated test passes from real infrastructure deployments.
2. Keep sample data fictional; don't commit secrets or client information.
3. Save commands, expected/actual status codes, and recovery observations.
4. Never present controlled fault injection as an actual employer incident.
5. Rerun after fixing failures; don't manually hide failing evidence.

## Recruiter reproduction

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m cloudops_lab demo --output evidence
```

Compare [generated JSON](../evidence/incident-replay.json) with source code and test expectations.

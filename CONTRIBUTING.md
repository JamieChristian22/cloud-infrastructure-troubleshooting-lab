# Contributing

Thanks for helping improve this engineering practice lab. Small, reproducible fixes are welcome.

1. Open an issue explaining the failure or missing scenario; include only synthetic data.
2. Create a feature branch and keep the change focused on one lab or runbook.
3. Run `python -m unittest discover -s tests -v` and `python -m cloudops_lab demo --output evidence`.
4. Add a regression test when changing runtime behavior.
5. Mark planned, mocked, simulated, and actually executed work honestly.
6. Open a PR with the commands you ran, expected and actual observations, and any security considerations.

We do not accept secrets, production artifacts, dependency attacks, unauthorized network scanning, or changes that expose the fault-control interface publicly.
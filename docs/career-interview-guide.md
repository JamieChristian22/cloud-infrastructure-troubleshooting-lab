# How to present this project in an engineering interview

## Thirty-second version

> I built a no-cost offline incident-response lab around a Python HTTP service with health checks, metrics, a command-line operations tool, four reproducible failure modes, and automated regression tests. I used it to practice distinguishing liveness from readiness, interpreting HTTP failures and response-time changes, restoring service health, and recording structured evidence. It's a simulated lab rather than production incident history.

## Technical walkthrough questions

**Why both liveness and readiness?**

The process can be alive while a dependency makes business requests fail. In the dependency-outage test, liveness remains HTTP 200 while readiness and the order API return HTTP 503. The difference informs alert routing and orchestration health checks.

**How did you investigate HTTP 500?**

Inject `application_error`, observe 500 from `/api/orders` while liveness remains 200, inspect request IDs and metrics, recover, and test the affected API again. The root cause is intentionally injected—there is no genuine exception stack trace to discover.

**Why is HTTP 200 not always healthy?**

A 200 does not prove acceptable latency or user experience. A high-latency fault adds approximately 300 milliseconds without changing the successful status code.

**What are the security assumptions?**

Fault controls require an unpredictable token and loopback binding by default; metrics use fixed route labels. These local teaching mitigations are not production identity or internet exposure controls.

**What would you build next?**

A real dependency, error budgets, bounded retries, alert routing, instrumented service-level objectives, ephemeral CI environments, and rollback. Review ownership, blast radius, costs, and access before provisioning anything.

## Five-minute demonstration

1. Explain the service topology and the location of fault state.
2. Run `python -m cloudops_lab serve` in terminal one.
3. Run `python -m cloudops_lab status` and `probe` in terminal two.
4. Inject `dependency_outage`; show liveness 200, readiness 503, API 503.
5. Recover; verify API 200, then open the replay report and tests.

## Accurate résumé language

**Appropriate:** Built and tested a local Python incident-response lab with simulated fault injection, health endpoints, metrics, structured logs, and automated recovery verification.

**Inappropriate:** Claims about actual customer outages, production AWS deployments, or measured downtime reductions that did not occur.

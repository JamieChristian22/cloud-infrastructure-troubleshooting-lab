# Engineering roadmap — scoped, testable, honest

## Phase 1 — Verified local incident simulator (completed)

- [x] Python service and synthetic API
- [x] Health/readiness endpoints and metrics
- [x] Four fault-injection workflows
- [x] SQLite-backed synthetic order service with real disconnect/reconnect
- [x] Request-duration Prometheus histograms
- [x] Token-protected local controls
- [x] CLI probes and recovery
- [x] Unit, integration, and end-to-end tests
- [x] Reproducible JSON and Markdown evidence
- [x] Read-only Linux and DNS/TCP diagnostics

## Phase 2 — Containers and operator workflows (partial)

- [x] Dockerfile with non-root user
- [x] Localhost-bound Compose configuration
- [x] Verify Docker image build and Compose smoke test via GitHub Actions
- [x] Verify container health checks and SQLite failure replay via GitHub Actions
- [ ] Add genuine screenshots or shell recording evidence

## Phase 3 — Deeper reliability engineering (planned)

- [x] Add a real in-memory SQLite database dependency and controlled disconnect/recovery
- [x] Expose Prometheus request-duration histograms
- [ ] Measure p50/p95/p99 against repeatable sustained test workloads
- [ ] Add bounded retries, backoff, timeouts, and circuit breakers
- [ ] Define SLO and error-budget policies
- [x] Add a Prometheus + Grafana local-only Compose overlay and provisioned dashboard
- [ ] Validate long-running dashboard behavior and meaningful alerting
- [ ] Validate resource limits and restart behavior

## Phase 4 — Cloud and DevOps (optional, planned)

- [ ] Add Terraform after cost and architecture review
- [ ] Run `terraform fmt`, `validate`, and `plan` before deployments
- [ ] Validate Kubernetes manifests locally
- [ ] Deploy to AWS only with explicit budget approval and teardown plan
- [ ] Produce actual deployment logs and post-deploy verification

**Acceptance rule:** A checkbox is completed only after the feature exists, was executed, and has saved evidence. No planned scope is presented as deployed.

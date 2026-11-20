# Engineering roadmap — scoped, testable, honest

## Phase 1 — Verified local incident simulator (completed)

- [x] Python service and synthetic API
- [x] Health/readiness endpoints and metrics
- [x] Four fault-injection workflows
- [x] Token-protected local controls
- [x] CLI probes and recovery
- [x] Unit, integration, and end-to-end tests
- [x] Reproducible JSON and Markdown evidence
- [x] Read-only Linux and DNS/TCP diagnostics

## Phase 2 — Containers and operator workflows (partial)

- [x] Dockerfile with non-root user
- [x] Localhost-bound Compose configuration
- [ ] Verify Docker image build and Compose smoke test
- [ ] Verify container health checks and failure replay
- [ ] Add genuine screenshots or shell recording evidence

## Phase 3 — Deeper reliability engineering (planned)

- [ ] Add a real local database dependency and controlled outages
- [ ] Measure p50/p95/p99 with request histograms and test workloads
- [ ] Add bounded retries, backoff, timeouts, and circuit breakers
- [ ] Define SLO and error-budget policies
- [ ] Add a Prometheus + Grafana local-only profile
- [ ] Validate resource limits and restart behavior

## Phase 4 — Cloud and DevOps (optional, planned)

- [ ] Add Terraform after cost and architecture review
- [ ] Run `terraform fmt`, `validate`, and `plan` before deployments
- [ ] Validate Kubernetes manifests locally
- [ ] Deploy to AWS only with explicit budget approval and teardown plan
- [ ] Produce actual deployment logs and post-deploy verification

**Acceptance rule:** A checkbox is completed only after the feature exists, was executed, and has saved evidence. No planned scope is presented as deployed.

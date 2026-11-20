# Published repository — maintenance and recruiter checklist

This project is **already published** at https://github.com/JamieChristian22/cloud-infrastructure-troubleshooting-lab. No new repository creation or Git bundle import is needed.

## Before sharing with employers

1. Check that the latest main-branch workflow in [GitHub Actions](https://github.com/JamieChristian22/cloud-infrastructure-troubleshooting-lab/actions) is green, including the Python version tests and Docker incident replay.
2. Read [verification](docs/verification.md) and distinguish local simulation from real cloud infrastructure.
3. Review [the source](src/cloudops_lab/), [runbooks](docs/runbooks/), [incident case studies](docs/incidents/) and [replay artifacts](evidence/).
4. Test the quick-start instructions on a fresh machine where possible.
5. Do not commit .env files, Grafana passwords, runtime control tokens or personal client data.
6. Use the [interview guide](docs/career-interview-guide.md) and link this repo to relevant cloud, platform, support and junior SRE applications.

## Maintenance

- Review dependency-update PRs individually; confirm their checks before merging.
- Keep deployed/verified checkboxes in [the roadmap](docs/roadmap.md) accurate.
- Label postmortems and screenshots with environment and evidence origin.
- Keep AWS/Terraform deployment optional and budget-controlled.

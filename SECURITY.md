# Security boundary and reporting

This project intentionally contains fault injection and simulated failure responses. It must not be exposed to the public internet or deployed to production.

- Run the service on `127.0.0.1` by default. Docker Compose explicitly publishes only to the host's loopback interface.
- Changing the bind to `0.0.0.0` requires `--allow-non-loopback` and is provided solely for the Docker container's network namespace; do not forward the container to a public interface.
- Fault-control endpoints require a randomly generated control token saved with local `0600` permissions in `.lab/control.json`. Never check the token into GitHub, paste it into an issue, or commit `.lab`.
- Demo order data and incident evidence are synthetic. Never put secrets, personal data, production exports, or client logs into evidence.
- The fault simulator is a **teaching lab**, not a hardened internet-facing service. No rate limiting, enterprise authentication, TLS termination, or persistence is implemented.

To report a security issue, contact the repository owner privately via their GitHub profile. Avoid posting exploitable details in public issues until acknowledged.
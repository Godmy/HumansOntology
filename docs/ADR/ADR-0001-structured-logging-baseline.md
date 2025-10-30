# ADR 0001: Structured Logging Baseline

- Status: Accepted
- Date: 2025-10-30
- Authors: Backend Team

## Context

We run the backend as a Starlette/GraphQL service inside Docker (dev, prod, CI). Until now logging was ad-hoc: console-only, mixed formats, duplicated Uvicorn access lines, and no predictable file output. Observability, troubleshooting in Docker Desktop, and auditing of request behaviour required a consistent approach.

## Decision

1. **Structured format**  
   Use `core.structured_logging.setup_logging` as the single bootstrap entry. Log records are emitted in JSON for files and condensed text for console. Every record carries contextual fields (`timestamp`, `level`, `logger`, `request_id`, `user_id`, plus request metadata from middleware).

2. **File handlers enabled by default**  
   `LOG_FILE_ENABLED=true` is now the default. We rotate `app.log`, `access.log`, and `error.log` under `/app/logs` (mounted in docker-compose). This ensures a persistent trail beyond ephemeral container output.

3. **Console signal-to-noise optimisation**  
   Docker stdout uses a compact text formatter (`LOG_CONSOLE_FORMAT`) and Uvicorn access logs are suppressed unless `LOG_SUPPRESS_UVICORN_ACCESS=false`. All access details are preserved inside our request middleware JSON entries.

4. **Request logging middleware**  
   `RequestLoggingMiddleware` pushes API activity through the structured logger, attaching request/response metadata, durations, and user IDs. Failures are tagged with `stage=exception`.

5. **Configuration surface**  
   Environment variables (`LOG_LEVEL`, `LOG_DIR`, `LOG_CONSOLE_JSON`, etc.) control behaviour. docker-compose injects sane defaults so local developers get the same baseline without manual exports.

6. **Operational visibility cookbook**  
   The middleware output (request body, timings) is now the primary signal path when other teams or AI agents investigate “slow dashboards”/“zeros in counters”. Keep the cookbook (see `docs/AI_COOKBOOK.md`) aligned with this ADR so that teams know which logs to grep and which toggles (`LOG_SUPPRESS_UVICORN_ACCESS`, `LOG_CONSOLE_FORMAT`) are safe to touch during production debugging.

## Consequences

- Easier debugging: Docker Desktop shows succinct lines while full JSON logs are archived in `backend_logs` volumes.
- Platform neutrality: the same configuration works for dev, CI, and production clusters.
- Slightly higher I/O due to file writes, but mitigated by rotation and async-friendly logging handlers.
- Future log streams (e.g., Loki, CloudWatch) simply tail the JSON files or STDOUT without code changes.

## References

- `packages/backend/core/structured_logging.py`
- `docker-compose*.yml` environment entries (`LOG_*`)
- `packages/backend/core/middleware/request_logging.py`
- `docs/AI_COOKBOOK.md`

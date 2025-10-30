# Task for Claude Sonnet 4.5: Database Enhancements

**Overview:**
This task aims to significantly improve database interaction within the backend application, covering query optimization, data migration tools, and automated backup/restore. The goal is to enhance performance, reliability, and data manageability.

**System Context:**
*   **Language:** Python
*   **Framework:** FastAPI
*   **ORM:** SQLAlchemy
*   **Database:** PostgreSQL
*   **DB Migrations:** Alembic
*   **CLI:** `click` (file `packages/backend/cli.py`)
*   **Logging:** Structured logging with `python-json-logger` (file `packages/backend/core/structured_logging.py`). A `log_database_query` function exists for logging queries and slow queries.
*   **Monitoring:** Sentry (`sentry-sdk[starlette,sqlalchemy]`) and Prometheus (`prometheus-client`) are used for monitoring.
*   **GraphQL:** `strawberry-graphql`
*   **Project Structure:** Monorepo with `packages/backend` for the backend.

**Current Implementation Status (What's already there):**

*   **Query Optimization:**
    *   Usage of `joinedload` in some places (`auth/services/admin_service.py`, `languages/services/dictionary_service.py`, `languages/services/search_service.py`) indicates awareness of the N+1 problem.
*   **Data Migration Tools:**
    *   `backup-db` and `restore-db` commands in `packages/backend/cli.py` for manual full DB dump/restore using `pg_dump` and `psql`.
    *   The `seed_data` command in `packages/backend/cli.py` has a `dry-run` mode.
*   **Automated Backup:**
    *   Manual `backup-db` and `restore-db` commands exist.

**What needs to be implemented (Acceptance Criteria for Claude):**

**1. Query Optimization & N+1 Prevention (#24)**
*   **SQLAlchemy relationship lazy loading review:** Conduct a full audit of `lazy loading` usage in SQLAlchemy models and queries.
*   **Add joinedload/subqueryload where needed:** Extend the use of `joinedload` and `subqueryload` for all critical queries where necessary to prevent N+1 problems.
*   **Query logging in DEBUG mode:** Integrate the existing `log_database_query` function from `core/structured_logging.py` with the SQLAlchemy query execution mechanism, so that all queries are logged at the DEBUG level. Ensure that `echo=False` in `core/database.py` does not prevent this, possibly by using SQLAlchemy events.
*   **Monitoring slow queries (>100ms):** Integrate the slow query monitoring logic (already present in `log_database_query`) with SQLAlchemy to automatically log warnings for queries exceeding 100ms.
*   **Indexes for frequently used fields:** Analyze the most frequently used fields in queries and add necessary indexes to SQLAlchemy models (via `__table_args__` or `Index`).
*   **Database query profiling tools:** Research and propose the integration of additional query profiling tools if Sentry and Prometheus are insufficient for deep analysis.
*   **GraphQL DataLoader integration:** Implement GraphQL DataLoader integration to optimize database queries executed via the GraphQL API, to avoid N+1 problems at the GraphQL layer.

**2. Data Migration Tools (#34)**
*   **Selective export (by entities, dates, filters):** Develop CLI commands for selective data export (e.g., by specific entities, date ranges, or using filters).
*   **Data transformation during migration:** Provide a mechanism for data transformation during migration (e.g., changing field formats, anonymization).
*   **Dry-run mode for verification:** Extend the `dry-run` mode for data export/import commands to allow verification of the outcome without actually modifying the database.
*   **Rollback mechanism:** Implement a rollback mechanism for data migration operations.
*   **Progress reporting for large datasets:** Add progress reporting for operations involving large datasets.

**3. Automated Database Backup & Restore (#27)**
*   **Daily backups to S3/local storage:** Implement automated daily database backups. Backups should be stored both locally and, if configured, in S3-compatible storage.
*   **Retention policy (7 daily, 4 weekly, 12 monthly):** Implement a backup retention policy (e.g., 7 daily, 4 weekly, 12 monthly).
*   **Point-in-time recovery:** Research and implement the ability to restore the database to a specific point in time.
*   **Backup verification (restore test):** Develop a mechanism for automatic verification of backup integrity (e.g., by restoring to a test database).
*   **Celery task for scheduled backups:** Integrate Celery (or a similar background task system) for scheduling and executing automated backups. `celery` needs to be added to `requirements.txt` and configured.
*   **CLI command for manual backup/restore:** The existing `backup-db` and `restore-db` commands should be enhanced to support new features (e.g., choice of storage location, application of retention policy).

**Expected Outcome:**
*   Updated backend code with implemented features.
*   Updated documentation describing new CLI commands, configuration, and operational principles.
*   Addition of necessary dependencies to `requirements.txt`.
*   Examples of using new features.

**Priority:** High.
**Estimated Effort:** 8 story points (as per original tasks).

---
**Additional Information for Claude:**

*   **Files to review:**
    *   `packages/backend/requirements.txt`: List of dependencies.
    *   `packages/backend/cli.py`: Existing CLI commands.
    *   `packages/backend/core/config.py`: Application configuration.
    *   `packages/backend/core/database.py`: DB connection setup.
    *   `packages/backend/core/structured_logging.py`: Logging system.
    *   `packages/backend/auth/models/user.py`, `packages/backend/languages/models/concept.py` (and other models): Examples of SQLAlchemy models.
    *   `packages/backend/auth/services/admin_service.py`, `packages/backend/languages/services/dictionary_service.py`: Examples of `joinedload` usage.

*   **Recommendations:**
    *   For SQLAlchemy query logging integration, consider using SQLAlchemy events (e.g., `before_cursor_execute`, `after_cursor_execute`) to intercept queries and pass them to `log_database_query`.
    *   For automated backups and Celery, new configuration files and modules may be required.
    *   When working with S3, use the `boto3` library.
    *   When creating new CLI commands, follow the existing style in `cli.py` using `click`.
    *   All changes must adhere to existing coding standards and project architecture.

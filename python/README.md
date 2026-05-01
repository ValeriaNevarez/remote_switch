# Python Jobs Runbook

This folder contains the production Python jobs that orchestrate remote-switch operations.

## Prerequisites

- Python 3.11+ recommended
- Install dependencies:
  - `pip install -r python/requirements.txt`
- Configure required secrets and config:
  - repo-level `config.json` (used by `repo_config.py`)
  - environment variables consumed by `env.py` (`*_B64`, API tokens, etc.)
  - helper scripts/docs in `python/secrets/`

## Environment Variables Checklist

Set these before running jobs (values omitted on purpose):

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TOKU_API_TOKEN`
- `FIREBASE_DATABASE_URL`
- `FIREBASE_SERVICE_ACCOUNT_B64`
- `GMAIL_OAUTH_CLIENT_B64`
- `GMAIL_TOKEN_B64`

Notes:

- `*_B64` variables are expected to contain base64-encoded UTF-8 JSON.
- Missing/empty values fail fast with clear runtime errors from `env.py`.
- Optional: set `LOG_LEVEL` (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

## Run Jobs Locally

From repo root:

- Daily call scheduler:
  - `python python/make_calls.py`
- Toku payment sync:
  - `python python/sync_with_toku.py`
- Weekly report email:
  - `python python/send_weekly_report.py`

PowerShell helper:

- `python/run-local.ps1` wraps local setup and script execution.

## Tests

From repo root:

- `python -m unittest discover -s python/tests -p "test_*.py"`

## Logging Runbook

Logs are single-line key=value events and can be filtered by `event=...`.
All scripts use Python's `logging` module with a shared formatter.

### make_calls.py

Prefix:

- `scheduler:`

Primary events:

- `event=call_decision`
  - Common fields: `phone`, `enabled`, `reason`
  - Common reasons:
    - `no_prior_call`
    - `last_call_not_completed`
    - `stale_completed_call`

### sync_with_toku.py

Prefix:

- `sync:`

Primary events:

- `event=toku_sync`
  - Common fields: `phone`, `client`, `action`
  - Common actions:
    - `skip` (typically `reason=no_toku_data`)
    - `noop`
    - `enable`
    - `disable`
    - `error`

### switch_caller.py

Prefix:

- `switch:`

Primary events:

- `event=call_start`
- `event=call_queued`
- `event=master_change_start`
- `event=master_change_sent`

### send_weekly_report.py

Prefix:

- `report:`

Primary events:

- `event=report_compiled`
  - Fields: totals for devices and report buckets
- `event=email_sent`
  - Fields: `message_id`, `to`

## Troubleshooting Tips

- No devices being called:
  - inspect `scheduler: event=call_decision` and `reason=...`
- Sync not toggling switches:
  - inspect `sync: event=toku_sync action=...` for `skip` and `noop`
- Weekly report not delivered:
  - verify `report: event=report_compiled` appears before `event=email_sent`
  - if `email_sent` is missing, validate Gmail token/env vars

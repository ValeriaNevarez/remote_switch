## Local secret files

- `firebase_private_key.json` — Firebase service account (input to `build_env.py` only)
- `firebase_db_url.txt` — one line, Realtime Database URL
- `gmail_oauth_client.json` — Gmail OAuth client (Desktop)
- `gmail_token.json` — Gmail authorized-user token (`token.json` style)
- `twilio_account_sid.txt` — one line, Account SID only (inputs to `build_env.py`)
- `twilio_auth_token.txt` — one line, auth token only

Not committed.

## Convert to environment variables

```bash
python secrets/build_env.py
```

These can be used for `run-local.ps1` or use the values for Github Action secrets.
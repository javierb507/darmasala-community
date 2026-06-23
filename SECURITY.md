# Security

## Environment Variables Required in Production

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | **YES** | Random secret for session signing. Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `SMTP_PASS` | If using email | SMTP password — never stored in the database |
| `DATABASE_URL` | For MySQL | `mysql://user:pass@host/dbname` (SQLite used in dev) |

## Default Credentials (Change Before Production)

- **Admin password:** `DarmaSala2025!` — set a strong password during setup:
  ```bash
  python init_db.py --admin-pass <your-secure-password>
  ```
- **`reset_admin.py`** uses `admin123` — development utility only, do not run in production.

## What Is and Is Not Stored in the Database

- **Stored:** SMTP host, port, username, sender address (non-sensitive)
- **Never stored:** SMTP password, SECRET_KEY, GitHub token — these must come from environment variables

## Reporting Vulnerabilities

Open an issue at https://github.com/javierb507/darmasala-community/issues with the label `security`.  
For sensitive disclosures, contact: javier.ballesteros@gmail.com

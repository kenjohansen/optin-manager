# OptIn Manager Backend

## Secure Data Storage Locations

- **Main Database (SQLite):**
  - File: `backend/optin_manager.db`
  - Used for all persistent relational data in local/dev mode.
- **Provider Secrets Vault:**
  - File: `backend/vault/provider_secrets.vault`
  - Encrypted at rest using strong symmetric encryption (Fernet/AES-256).
  - Only accessible by backend service; never exposed to frontend or committed to git.
  - All secrets updates and access are logged and auditable.

---

## CORS Configuration (Development & Production)

### Development
- The backend is configured to allow all origins for local development. This avoids CORS errors when the frontend runs on different ports (e.g., Vite dev server).
- **Location:** `backend/app/main.py`
- **Current Setting:**
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],  # Development: allow all origins
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

### Production
- **IMPORTANT:** For security, you must restrict `allow_origins` to your actual frontend URLs in production.
- **Example:**
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["https://your-frontend.com"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
- Never use `allow_origins=["*"]` in production, as it allows requests from any origin and is a security risk.

---

## Development Server Management (Frontend & Backend)

To ensure you never have port conflicts, zombie processes, or multiple dev servers running:

### Kill All Dev Processes

Use this script to kill all backend and frontend dev processes (uvicorn/python/node/npm) and free ports 8000/5173:

```bash
./kill-all.sh
```
- Kills all OptIn Manager backend (uvicorn/python) and frontend (npm/node) dev processes.
- Frees up ports 8000 (backend) and 5173 (frontend).

### Start Both Backend and Frontend

Use this script to kill all previous dev processes and start both backend and frontend cleanly:

```bash
./run-dev.sh
```
- Always runs `kill-all.sh` first.
- Starts backend (uvicorn) and frontend (`npm run dev`) in the background.
- Installs dependencies if missing.
- Prints process IDs and status.

**Tip:**
- Never use `npm start` for the frontend; always use `npm run dev` (handled by the script).
- If you see port conflicts or duplicate processes, just run `./kill-all.sh` and then `./run-dev.sh` again.

---

## Database and Migrations (Bulletproof Workflow)

### Supported Databases
- **SQLite:** Uses `optin_manager.db` in the backend directory (default for dev/local).
- **PostgreSQL:** Uses schema `optin_manager` for all tables. Set `DATABASE_URL` env var for connection.

### One-Command Migration
To apply all migrations (create or upgrade DB schema):

```bash
./scripts/upgrade_db.sh
```
- Works for both SQLite and PostgreSQL.
- For PostgreSQL, set `DATABASE_URL` in your environment first.

### Changing the Schema
1. Edit your SQLAlchemy models in `app/models/`.
2. Generate a migration:
   ```bash
   alembic revision --autogenerate -m "Describe your change"
   ```
3. Apply migrations:
   ```bash
   ./scripts/upgrade_db.sh
   ```
4. On backend start, you will see logs for:
   - The DB URL in use
   - The current Alembic migration version
   - Whether the default admin user was created

### Admin User Creation
- On backend startup, if the `auth_users` table is empty, a default admin user is created:
  - **Username:** `admin`
  - **Password:** `TestAdmin123`
- Change this password immediately after first login.

### PostgreSQL Schema Support
- All tables are created in the `optin_manager` schema.
- Ensure your PostgreSQL user has permission to create schemas/tables.
- Example `DATABASE_URL`:
  ```
  export DATABASE_URL=postgresql://user:pass@host/dbname
  ```

### Troubleshooting
- If you see migration/version errors, run `./scripts/upgrade_db.sh`.
- Always check backend startup logs for DB and migration status.
- Do **not** delete the DB file to fix schema issues—use migrations!

### Model/Migration Sync
- Always generate a migration after changing models.
- Never edit the database schema manually.

---
For further help, see the Alembic docs: https://alembic.sqlalchemy.org/

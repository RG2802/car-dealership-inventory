# Apex Motors — Car Dealership Inventory

A full-stack inventory kata built with **FastAPI, file-backed SQLite, React, Vite and Tailwind CSS**. Buyers register, sign in, search the collection and purchase stock. Administrators get inventory forms, restocking and deletion controls.

Purchasing is an inventory operation, not a payment or checkout integration. All prices use USD. Demo entries are fictional: six manually authored sample rows, not scraped listings or a real dealership dataset. Vehicle artwork is original inline SVG illustration, not a photo of an actual listing.

## Run locally

Requires Python 3.12+ and Node.js 22+ with npm. Start both processes from the extracted project.

### Backend (terminal 1, project root)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
export JWT_SECRET="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export DATABASE_PATH=data/dealership.db
python -m backend.manage seed
python -m backend.manage create-admin --email admin@example.com
uvicorn backend.app:create_app --factory --reload --host 127.0.0.1 --port 8000
```

`seed` is optional and refuses to run on nonempty inventory. The admin command prompts for a password; it refuses duplicate accounts and never silently promotes a buyer. Register ordinary buyers through the UI. There is no default production password.

Windows PowerShell: activate with `.venv\Scripts\Activate.ps1`; set variables with `$env:JWT_SECRET = python -c "import secrets; print(secrets.token_hex(32))"` and `$env:DATABASE_PATH = "data/dealership.db"`. The remaining Python commands are identical.

`.env.example` documents configuration; the application does **not** automatically load `.env`. Export variables in your shell. Keep the same JWT secret between restarts if existing tokens must remain valid. The database survives restarts at the configured file path.

API documentation: http://127.0.0.1:8000/docs

### Frontend (terminal 2)

```bash
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Open http://127.0.0.1:5173. Vite proxies `/api` to port 8000. For a production frontend build, run `npm run build`; serve `frontend/dist` behind a web server that proxies `/api` to FastAPI. A static frontend deployment by itself is insufficient. Hosting must provide persistent disk for SQLite, or the repository must be adapted to PostgreSQL. No live deployment is included.

## Architecture and behavior

- `backend/app.py`: app factory, HTTP endpoints and authorization dependencies.
- `backend/schemas.py`: strict request contracts and validation.
- `backend/security.py`: Argon2 password hashing and JWT issuance.
- `backend/db.py`: SQLite schema and transaction/connection lifecycle.
- `backend/inventory.py`: parameterized inventory queries and atomic stock updates.
- `backend/manage.py`: trusted administrator creation and optional demo seeding.
- `frontend/src/main.jsx`: authentication, dashboard, filters and inventory dialogs.
- `frontend/src/VehicleCard.jsx`: reusable inventory cards and SVG vehicle artwork.
- `frontend/src/api.js`: authenticated API calls and error normalization.

Passwords are never returned or stored in plaintext. JWTs expire after one hour; the signing secret must be at least 32 characters. Roles are read from the database on each request. Public registration rejects extra fields, including `role`. Tokens remain in browser memory; a page refresh requires signing in again. Logout removes the client session; there is no server-side token revocation list.

Prices are validated to two decimal places, stored as integer cents and serialized as numeric USD. Quantities are strict integers from zero to one million. Stock changes require positive integer quantities. Purchases use `UPDATE ... WHERE quantity >= ?` in a transaction, avoiding read-then-write overselling. A failed stock update returns 409; missing vehicles return 404.

A PUT replaces all vehicle details, including quantity, as requested by the kata. It can overwrite a concurrent inventory change; a production system should separate stock adjustments, use version checks, and keep an audit ledger. Purchases do not have idempotency keys: intentionally repeating a successful request buys another unit. The UI disables purchase buttons during requests and for zero stock.

Search combines make, model and category with case-insensitive literal substring matching plus inclusive minimum/maximum price. Search uses bound parameters; `%` and `_` are literal characters. Results include out-of-stock entries so buyers can see availability. Dashboard totals reflect the filtered results.

## Endpoint permissions

| Endpoint | Access | Result |
| --- | --- | --- |
| POST `/api/auth/register` | Public | 201 + user and access token |
| POST `/api/auth/login` | Public | 200 + user and access token |
| GET `/api/auth/me` | Signed in | Current account |
| GET `/api/vehicles` | Signed in | All inventory rows |
| GET `/api/vehicles/search` | Signed in | Filtered inventory |
| POST `/api/vehicles` | Signed in | 201 + created vehicle |
| PUT `/api/vehicles/{id}` | Signed in | Updated vehicle |
| DELETE `/api/vehicles/{id}` | Admin | 204 |
| POST `/api/vehicles/{id}/purchase` | Signed in | Updated stock |
| POST `/api/vehicles/{id}/restock` | Admin | Updated stock |

The brief explicitly restricts **delete and restock** to admins; add/update API access is available to any signed-in account. The SPA only exposes management forms to admins, matching its separate UI requirement. Hiding UI is not an authorization control. For a stricter business policy, change the add/update dependencies to `admin_user` and change the tests together.

Vehicle body:

```json
{"make":"Toyota","model":"Camry","category":"Sedan","price":"32500.25","quantity":6}
```

Stock operation body: `{"quantity":1}`. Search example: `/api/vehicles/search?make=toyota&category=sedan&min_price=20000&max_price=40000`.

## Tests and TDD evidence

```bash
# Project root, virtual environment activated
python -m pytest --cov=backend --cov-branch --cov-report=term-missing --cov-report=html
cd frontend
npm test
npm run build
npx playwright install --with-deps chromium
npm run test:e2e
```

Browser tests start isolated backend/frontend processes on ports 8000 and 5173; stop your development servers first. The test backend uses a temporary on-disk database and disposable credentials. The Playwright config assumes the Unix `.venv/bin/python` path; on Windows change that command to `.venv/Scripts/python.exe`.

See [TEST_REPORT.md](TEST_REPORT.md) and raw test logs in `docs/`. Backend coverage includes the management CLI but excludes test files and the disposable browser server; the enforced minimum is 95%.

The Git history preserves actual red/green runs for authentication, inventory and frontend card contracts, followed by refactoring. Initial authentication red is a missing-module collection failure; inventory red includes actual failing assertions. Later management/security regression checks were added after those features; not every line was produced through TDD. Commits and logs are not backdated. The archive includes `.git` and a portable Git bundle for preserving the history.

## Screenshots

Screenshots are **not included**: this execution environment denied a local socket operation required by Chromium, so the browser exited before screenshots could be captured. The browser tests are included but have not passed here. This is an outstanding deliverable, not a completed visual verification.

Run `npm run test:e2e` locally to generate `docs/dashboard-desktop.png`, `docs/dashboard-mobile.png` and `docs/login.png`. Inspect those screenshots, then add them to the repository and embed them here before submission.

## My AI Usage

**Tool used:** OpenAI ChatGPT/Codex, acting as the coding assistant in this conversation. No Copilot, Gemini or external project repository was used.

**How it was used:** The assistant selected the architecture, authored tests before the initial authentication/inventory/card implementations, wrote backend and frontend code, ran the test suites and production build, debugged environment problems, created the original SVG artwork, and drafted this documentation. The user supplied the kata brief. These are substantial AI contributions; this is not a claim that the user manually implemented or reviewed the code.

**Reflection:** AI accelerated the initial implementation and made it practical to test authorization, validation and concurrent purchasing together. It also required verification: browser installation and execution exposed environment issues, and API/UI permission ambiguities needed an explicit decision. Passing tests do not establish production readiness. The candidate should review every module, run the app independently, modify a feature and explain the tradeoffs before submitting it. This reflection is an assistant-authored disclosure, not a fabricated personal statement from the candidate.

**Attribution limitation:** This workspace disables AI commit co-author attribution. Consequently, the generated commits do not contain the co-author trailers requested by the kata, although AI usage is disclosed here. This deliverable does not satisfy that submission rule as-is. Do not claim otherwise.

**Conversation evidence:** See [PROMPTS.md](PROMPTS.md). A genuine ChatGPT export/public conversation link still needs to be added by the account holder; a reconstructed summary is not a raw transcript.

## Publication and submission status

This is a local working project, not a published repository. No destination repository was supplied and the available repository integration does not create repositories. Create an empty public repository, then from this project run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Do not submit placeholder URLs. Local commits use `Project Builder <builder@example.invalid>`, not an invented identity for the candidate. Configure your own Git author for subsequent commits. If using the bundle instead of the included working tree: `git clone dealership-history.bundle dealership`.

Before submission, run the browser suite successfully, add real screenshots, provide the real public URL and authentic raw-chat export/link, and resolve the disclosed commit-attribution mismatch. Optional live deployment is not included.

## Scope limits

This kata does not implement payment processing, order history, refunds, email verification, password resets, rate limiting, pagination, migrations, an inventory audit ledger or production monitoring. SQLite is suitable for this single-instance exercise, not a claim of horizontally scalable dealership operations. Use HTTPS and managed secrets when deploying.

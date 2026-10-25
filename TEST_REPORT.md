# Test report

Executed on 25 October 2026. These are local results, not claims about a hosted CI run.

| Check | Result | Evidence |
| --- | --- | --- |
| Backend pytest suite | **54 passed** | `docs/backend-tests.txt`, `docs/backend-junit.xml` |
| Backend statement/branch coverage | **99.15% combined** | `docs/backend-tests.txt` |
| React component tests | **5 passed** | `docs/frontend-tests.txt` |
| Vite production build | **Passed** | `docs/frontend-build.txt` |
| Playwright browser tests | **Blocked / not passed** | `docs/browser-results.json` |
| Screenshots and visual inspection | **Not completed** | Chromium could not start |

Coverage includes API routes, SQLite repository, schema, security and operator CLI. Test modules and the disposable E2E server are excluded. The one uncovered executable line is the CLI `if __name__ == '__main__'` entry call. Coverage percentage does not imply complete security or production readiness.

Meaningful backend cases include registration, case-insensitive duplicate email rejection, Argon2 hashing, invalid and expired JWT rejection, deleted-user token rejection, public role-escalation rejection, protected-route access, admin-only deletion/restocking, literal and case-insensitive filters, price range validation, price precision, strict integer quantities, nonexistent vehicle handling, disk persistence across application instances, stock exhaustion, stock cap and eight concurrent purchases for two units (exactly two successes and six conflicts).

Component tests verify sold-out disabled buttons, selected-vehicle purchase callbacks, hidden buyer management controls, visible admin controls and request-in-progress disabled buttons.

## TDD evidence

- `docs/01-auth-red.txt`: initial authentication tests fail to import the not-yet-created implementation.
- `docs/02-auth-green.txt`: 10 authentication tests pass.
- `docs/03-inventory-red.txt`: inventory contracts fail before implementation.
- `docs/04-inventory-green.txt`: 49 combined tests pass after implementation.
- `docs/05-refactor-green.txt`: fixture refactor preserves behavior.
- `docs/06-frontend-red.txt`: card tests fail before the component exists.
- `docs/07-frontend-green.txt`: five card tests pass.

Git commits preserve the order. Later regression and operator-command checks were added after the initial implementation; this is explicitly not a claim of universal test-first development.

## Browser limitation

The browser suite starts an isolated file-backed SQLite API and a Vite frontend. The available Chromium download was installed through a fallback source. A direct launch diagnostic then reported:

```text
FATAL:process_singleton_posix.cc(292)
Check failed: . socket() failed: Operation not permitted (1)
```

The browser exited before UI assertions or screenshots could complete. `docs/browser-results.json` contains failure details. No screenshots are fabricated. Re-run on an unrestricted local development machine with `npx playwright install --with-deps chromium`, followed by `npm run test:e2e`; review the app at desktop and mobile widths. The optional `CHROMIUM_PATH` environment variable selects a locally installed executable, but normal local runs should use Playwright's installed version.

## Warnings

The installed Starlette emits an httpx TestClient deprecation warning; it did not cause failures. npm emitted an environment proxy configuration warning. Neither warning is represented as a passing browser check.

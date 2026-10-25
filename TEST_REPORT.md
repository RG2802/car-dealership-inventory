# Test Report — Car Dealership Inventory System

## Local verification

Verified on Windows on 25 October 2026.

| Check | Result |
| --- | --- |
| Backend tests | 54 passed |
| Backend combined statement/branch coverage | 99.15% |
| Frontend component tests | 5 passed |
| Browser end-to-end tests | 2 passed |
| Production build | Passed |
| npm audit | 0 reported vulnerabilities |

These results are from local execution, not a hosted CI run.
The npm audit result reflects the installed dependencies and
advisory database at the time of verification.

## Environment

- Windows
- Python 3.12.10
- Node.js 24.22.1
- npm 11.19.1
- pytest 9.1.1
- Vitest 5.0.5
- Vite 6.4.5
- Playwright with Chromium

## Backend testing

All 54 tests passed.

The tests cover:

- Registration, login and Argon2 password hashing.
- Case-insensitive duplicate email rejection.
- Request validation and rejection of public role escalation.
- Missing, invalid and expired authentication tokens.
- Rejection of tokens belonging to deleted users.
- Protected endpoints and administrator-only operations.
- Vehicle creation, updates, deletion and searching.
- Price precision and strict integer quantity validation.
- Database persistence across application instances.
- Purchasing, restocking and insufficient-stock handling.
- Stock limits and missing vehicles.
- Concurrent purchasing without overselling.
- Administrator creation and demo-data seeding.

The concurrency test submits eight purchases against two available
units and verifies exactly two successes and six stock conflicts.

Combined statement/branch coverage was 99.15%, exceeding the
configured 95% minimum.

Coverage includes application code and the management CLI.
Test modules and the disposable browser-test server are excluded.
The uncovered executable line is the management CLI entry-point call.

A Starlette/httpx deprecation warning was reported.
It did not cause a test failure.

## Frontend component testing

All five tests passed:

1. Purchase is disabled when stock is zero.
2. Purchase targets the selected vehicle.
3. Management controls are hidden from customers.
4. Management controls are visible to administrators.
5. Purchase is disabled while a request is pending.

## Browser end-to-end testing

The latest Windows run completed with two passing tests in 7.9 seconds.

### Administrator workflow

Verified:

- Administrator login.
- Inventory display.
- Mobile layout without horizontal overflow.
- Vehicle creation.
- Purchasing the final available unit.
- Disabled purchasing after stock reaches zero.
- Restocking.
- Editing vehicle details.
- Filtering inventory.
- Deleting a vehicle.
- Resetting filters.
- Logout.

### Customer workflow

Verified:

- Customer registration.
- Inventory display.
- Hidden administrator controls.
- Disabled purchasing for an out-of-stock vehicle.
- Purchasing an available vehicle.
- Visible purchase confirmation.

The browser suite uses a temporary, file-backed SQLite database
and disposable test accounts.

## Browser-test fixes and portability

The following issues were resolved during local verification:

- Corrected the backend Python executable path for Windows.
- Made the backend command select its Python path according to
  the operating system: Windows or Linux.
- Updated the login button selector to accommodate its arrow icon.
- Updated the purchase-confirmation selector to distinguish the
  success message from the simultaneous loading status.

The purchase-confirmation test now locates the status message
containing "Purchase recorded", avoiding an ambiguous match when
the inventory loading message is also visible.

Both tests passed after these changes.

The Windows branch of the configuration has been verified locally.
The Linux branch is configured for GitHub Actions but has not yet
been verified by a hosted CI run.

## Screenshots

Playwright generated:

- docs/dashboard-desktop.png
- docs/dashboard-mobile.png
- docs/login.png

The project owner manually reviewed all three screenshots and
reported that their appearance was satisfactory.

## Dependency audit and production build

Vitest and Vite were updated during local verification to address
reported dependency vulnerabilities.

After the updates:

- npm audit reported zero vulnerabilities.
- All five frontend component tests passed.
- The Vite production build completed successfully.

npm also reported an esbuild install-script warning.
The recorded test and build commands nevertheless completed
successfully.

## TDD evidence

The Git history and original logs preserve the initial development
sequence:

| Log | Recorded stage |
| --- | --- |
| docs/01-auth-red.txt | Authentication tests before implementation |
| docs/02-auth-green.txt | Authentication tests passing |
| docs/03-inventory-red.txt | Inventory tests before implementation |
| docs/04-inventory-green.txt | Inventory tests passing |
| docs/05-refactor-green.txt | Tests passing after fixture refactoring |
| docs/06-frontend-red.txt | Component tests before implementation |
| docs/07-frontend-green.txt | Component tests passing |

The initial authentication red run was a missing-module collection
failure. Inventory tests included failing assertions before their
implementation existed.

Later regression checks and browser-test corrections were added
after the initial features. Not every change followed test-first
development.

Original logs record earlier runs. The local verification results
in this report reflect the subsequent Windows executions.

## Earlier execution limitation

Browser execution was initially blocked in the assistant's
environment by a denied socket operation required by Chromium.

This limitation did not prevent subsequent local Windows testing.
The browser suite and screenshot generation have now completed
successfully on the project owner's computer.

## Limitations

Passing tests and a clean npm audit do not establish complete
security or production readiness.

Payment processing, load testing, independent security testing
and live deployment verification are outside the scope of these
checks. Hosted GitHub Actions verification remains pending.

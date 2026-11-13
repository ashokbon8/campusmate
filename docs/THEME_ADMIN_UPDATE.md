# Midnight, white and lime update

## Changes

- Midnight black `#080A0B` backgrounds, pure white `#FFFFFF` text and lime green
  `#C6FF00` accents across the homepage, CSS mascot, student sign-in, chat,
  noticeboard, tickets and admin workspace. Filled lime buttons use black text.
- Admin Login is visible in the header and footer, including before student
  sign-in. Its page has email/password fields, a password-visibility toggle and
  a back-to-home action.
- A stored admin token is verified before dashboard controls are rendered.
  Student and staff JWTs are isolated even if their accounts share an email.
- `SETUP_ADMIN.cmd` prompts locally for an administrator email and a masked
  password, preserves other environment settings and saves them privately.
  Restart/start the backend afterwards to create or update that admin account.
- Existing JSCOE FAQs and college data are retained.

## Apply to an existing installation

Stop both running servers and back up your project. Extract this package and
copy its code into your existing `campusmate` folder, choosing to replace code
files. Keep your existing `.env`, database and `storage` files. For a new admin
account, run `SETUP_ADMIN.cmd`, then `START_CAMPUSMATE.cmd`. Open
http://localhost:5173 and click Admin Login using the credentials you selected.

The Windows launchers require Python 3.12 or 3.11, and Node.js for the frontend.
No admin password is included in this archive.

## Validation

- Backend: 163 tests passed.
- Browser fallback engine: 15 tests passed.
- Production frontend build passed.
- React server rendering passed for the updated homepage, header and admin
  login, including the password field, navigation and local setup guidance.
- Existing data snapshots still match between backend and frontend.
- A full interactive browser check and execution of the Windows launchers were
  not possible in this Linux execution environment. Review the running pages
  on Windows before publishing.

This package does not push to GitHub or deploy a live website.

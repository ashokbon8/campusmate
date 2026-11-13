# JSCOE upgrade validation — 13 November 2026

- Backend: **157 tests passed**, including 25 new tests for the real source pack.
- Frontend saved-data engine: **15 tests passed**.
- Production frontend: `npm run build` passed.
- Original 50-question synthetic regression harness: every expected state passed;
  this harness is not a measurement of real-world JSCOE answer accuracy.
- Manual source review: fee scan and calendar image were visually inspected;
  admission checklist/procedure and examination index were read from the
  college website. No current deadlines were inferred from archived exam PDFs.
- Browser automation: not completed. Chromium could not launch because this
  execution environment blocks its Unix socket. Backend behaviour and the
  frontend fallback were tested independently; an interactive browser review
  on the user's Windows machine is still needed.
- Windows launcher: supplied for Python 3.12/3.11 + Node.js; not executed on
  Windows in this Linux workspace.

No GitHub push or production deployment was performed from this workspace.
The archive excludes credentials, user databases, virtual environments,
dependencies, and temporary test data.

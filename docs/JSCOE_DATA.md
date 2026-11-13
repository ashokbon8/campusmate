# JSCOE source pack

The 29 FAQs were reviewed against the following public college sources on
**13 November 2026**. This date records verification, not publication. The pack
is a dated snapshot; no scheduled scraping is performed.

| Source | Format | What is included |
| --- | --- | --- |
| [Document checklist](https://jspmjscoe.edu.in/admissions/documents-checklist) | Webpage | All 13 listed document types, two colour photos, conditional-certificate caveat and published admissions contacts |
| [Admission procedure](https://jspmjscoe.edu.in/storage/Admission/AdmissionProcedure.pdf) | Text PDF | CAP process overview and the undated guide's eligibility statements; no invented current CAP deadlines |
| [Fee structure 2026–27](https://jspmjscoe.edu.in/storage/Admission/FeeStructure2026-2027.pdf) | Scanned PDF, visually transcribed | B.E, M.E, MBA and MCA tuition/development totals and the printed category/gender groups |
| [Academic calendar index](https://jspmjscoe.edu.in/Academics/AcademicCalendar) / [FY 2026–27 image](https://jspmjscoe.edu.in/storage/NAAC/AcademicCalenderOddSemesterAY2026-27.jpg) | Image, visually transcribed | All 18 events in FY B.Tech odd semester, including the cross-year exam window and next-semester commencement |
| [Examination notices](https://jspmjscoe.edu.in/information_corner/exam) | Webpage | A clearly historical index summary; the listed notices are labelled 2024/2025 |

## Limits of the sources

- The checklist's category columns do not provide readable applicability flags.
  The bot lists documents but does not decide reservation eligibility.
- The admission PDF is undated. Current CAP eligibility/round rules must be
  checked against the current competent-authority brochure.
- Posted fee rows are not a student's personal balance or a determination of
  scholarship eligibility. Hostel/transport fees, instalment rules, refunds and
  fee deadlines are not supported by this table.
- The calendar provides a planned examination **window**, not a paper-by-paper
  timetable, time, room or hall assignment. Semester II's full calendar is not
  included just because its commencement appears in Semester I's calendar.
- No current exam-form deadline is inferred from archived 2024/2025 notices.
- College activities remain an available category for staff uploads. No event
  registration instructions were invented to fill this category.

## Maintain the bundled FAQs

1. Review the original sources, including scans, for the right year.
2. Edit `backend/app/data/jscoe_knowledge.json`. Retain each stable `id`, source
   URL/format and truthful checked date. Keep programme/year/semester scope.
3. Run `python scripts/sync_jscoe_data.py` from the project root.
4. Run the regression tests and frontend build.
5. In the backend's existing environment, run
   `python ../scripts/import_jscoe.py --refresh` from `backend` to intentionally
   refresh an already-imported entry. Normal startup leaves staff edits and
   retirements alone.

Website imports do not require an LLM or embedding API key. Each bundled FAQ is
indexed as a complete answer to preserve list/table rows. Retrieval recognises
programme aliases, explicit year/semester context and common question variants.
Live staff notices still use the regular retrieval and publication workflow.

## Validation

```bash
python -m pytest
python tests/run_validation.py
cd frontend
npm test
npm run build
```

The legacy 50-question validation harness uses synthetic fixtures explicitly;
its metrics are not measurements of the JSCOE dataset. New tests check sourced
fees/calendar facts, all checklist rows, source formats, safe unknowns, and
non-destructive imports into an existing database.

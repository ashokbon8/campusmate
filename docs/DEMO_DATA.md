# Demo data

Every notice that ships with this build is **synthetic sample data**. It exists
so the whole application — upload, indexing, retrieval, citations, version
replacement, tickets — can be demonstrated without any real college
information.

**Nothing here is a real examination schedule, fee deadline, timetable, or
college notice.** Each generated PDF starts with the line
`[SAMPLE DEMO DATA] This is not an official college document.`, and every
document title ends with `(sample)`.

## Seeded notices

The seed (`backend/app/services/seed.py`) creates six notices, one per
information area plus a superseded/current pair for Examinations:

| Title | Category | Version | Status |
| --- | --- | --- | --- |
| Admissions document checklist (sample) | Admissions | 1 | published |
| Fee payment information (sample) | Fees | 1 | published |
| Sample Mathematics examination notice (superseded) | Examinations | 1 | replaced |
| Sample Mathematics examination notice (current) | Examinations | 2 | published |
| Weekly timetable sample | Timetables | 1 | published |
| Campus activity registration (sample) | College activities | 1 | published |

The examination pair demonstrates version replacement: version 2 supersedes
version 1, so the chatbot answers from version 2 and labels version 1 as
`replaced`.

Each notice is written as a real, openable PDF into `UPLOAD_DIR` so the source
viewer has a file to display.

## How sample data is surfaced in the UI

- The chatbot shows a "SAMPLE DATA" tag on answers (`is_sample_data: true`).
- The footer states "Synthetic sample data only".
- The source viewer labels the document as sample.
- The validation/testing page separates proposed targets from measured demo
  results and notes the data is synthetic.

## The example conversation

The presentation's example conversation is reproduced as a demonstration:

1. Student: "When is my exam?"
2. CampusMate: "Which programme, semester and subject?"
3. Student: "BSc CS, Semester 1, Mathematics."
4. CampusMate: "The Mathematics examination will be held on 10 December 2026 at
   10:00 AM in Room 204." — source: sample examination notice v2, page 1,
   published 3 November 2026, replaces version 1.

This is synthetic. It is never presented as a real schedule.

## Removing the sample data

Set `CAMPUSMATE_SEED=0` before first start to begin with an empty database, or
delete `campusmate.db` (SQLite) / the database volume (Docker) and restart with
seeding disabled.

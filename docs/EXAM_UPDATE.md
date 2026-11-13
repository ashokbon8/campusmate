# Exam dates for all subjects

## Apply the update to your current project

1. Close the running CampusMate backend and frontend windows.
2. Extract `CampusMate_Exam_Update.zip` inside your existing `campusmate` folder.
   An extra extracted subfolder is fine; the updater checks its parent folders.
3. Open the extracted update folder and double-click `APPLY_EXAM_UPDATE.cmd`.
   If it cannot locate the project, paste the path to the folder containing
   both `backend` and `frontend`.
4. Run your existing `START_CAMPUSMATE.cmd` and refresh http://localhost:5173.

The updater backs up the previous code. It does not overwrite `.env`, your
database, uploaded documents, dependencies or the admin account. No extra Python
or npm dependency is added, and no database migration is required.

## Add your own dates for every subject

Open **Admin Login → Exam timetable**. Select programme, semester, academic year
and, if needed, division/group. Choose the exam type, then enter each subject's
date. Time and room are optional. **Load first-year subject names** helps with
the FY list; you can remove unused subjects or type any other subject, including
later-semester courses. Add abbreviations such as OS or DSA in Other names.

Click **Save and publish timetable**. The bot can now answer questions such as:

- When was my sem 1 math exam?
- When is my first semester physics exam?
- When is the chemistry paper?
- Show all semester 1 exam dates
- When is my sem 3 OS exam?

Dates saved here are labelled **admin-entered**. The editor can reload the
current timetable. Saving the same programme/semester/year/group/exam type
publishes a replacement; superseded dates stop answering student questions.
Use distinct division/group values for classes or branches with different dates.

## Try the supplied example dates

In the chatbot, click **Try demo exam dates**, or choose
**Exam date source → DEMO — example dates** and set B.Tech, semester 1 or 2,
academic year 2026–27. These examples cover all 18 subject names in the
reviewed FY course catalog, with 25 example rows across the two sample terms.
The chat answer, badge and source page explicitly mark the dates as fictional.
They are not inserted into the college notices or presented as real exam dates.

Return to **College + admin timetable** for published notices and the dates you
entered. New admin dates require the connected backend. The offline fallback
still answers from the saved college calendar or the explicit demo examples.

## What the official sources establish

- [JSCOE FY B.Tech 2026 syllabus, contents page](https://jspmjscoe.edu.in/storage/PDF/engineering%20science/syllabus/SyllabusStructureFYBTech2026Pattern.pdf):
  subject names and course codes. Shared subjects depend on the college's group
  and semester arrangement. The syllabus does not establish exam dates.
- [FY 2026–27 Semester I calendar](https://jspmjscoe.edu.in/storage/NAAC/AcademicCalenderOddSemesterAY2026-27.jpg):
  a planned end-semester examination window of 23 December 2026–7 January 2027,
  not an exact day/time for each paper.
- [Examination notice index](https://jspmjscoe.edu.in/information_corner/exam):
  the public listings checked on 13 November 2026 are labelled 2024/2025.
  Those old form notices were not used as current subject-wise dates.

If only the calendar is available, the bot now returns that clearly scoped
window and explains the missing paper date, asking for relevant context. It
does not immediately send an ordinary subject/date query to the helpdesk.

## Validation

186 unique backend tests passed (the full 182-test suite and four additional
installer/later-semester/knowledge-version checks), plus 55 frontend tests. Production build and
React server rendering passed. These are regression results, not an accuracy
measurement against a live college timetable.

Backend/installer tests cover all FY subject queries, all 25 demo rows,
arbitrary later-semester subjects, existing FAQ aliases, exact admin dates,
replacement, duplicate rejection, group/year separation, authentication and
preservation of user data by the installer. Frontend tests cover the same
wording and demo isolation. The production build and React rendering checks
were also run. Interactive browser and Windows execution still require review
on the target computer.

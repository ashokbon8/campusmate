# CampusMate Final — open and run

For the **GitHub hackathon submission and public website**, start with
[PUBLISH_ONLINE.md](PUBLISH_ONLINE.md). The local run below is still included.

## Run in VS Code

1. Install Python 3.12 if it is not already installed. Python 3.11 also works.
2. Extract **CampusMate_Final.zip** completely into a new folder. The extracted
   folder directly contains `RUN_CAMPUSMATE.cmd`, `backend` and `frontend`.
3. In VS Code, choose **File → Open Folder** and select that extracted folder.
   You can also open `Open_CampusMate.code-workspace`.
4. Open **Terminal → New Terminal** and run:

```powershell
.\RUN_CAMPUSMATE.cmd
```

That command installs the Python requirements, creates your local configuration,
sets up the admin account if needed, loads the included college data, and starts
the website and API together. The browser opens at **http://localhost:5173**.
Keep the terminal open. Press **Ctrl+C** to stop CampusMate.

The final ZIP includes the built website. **Node.js is not needed to run it.**
An internet connection is needed for the first Python-package installation.
No AI API key or paid service is required.

## First launch: choose your admin login

The first launch asks for a display name, an admin email, a password of at least
12 characters, and password confirmation. Password typing is visible locally
so you can see what you entered. Invalid input asks you to try again.

After setup, choose **Admin Login** in the website header. Students can create
their own accounts through **Create account**. Later launches use the saved
configuration and do not ask you to create the administrator again.

Private settings are created automatically in `backend/.env`. You do not need
to edit `.env.example`. To deliberately reset the administrator later, run:

```powershell
.\RUN_CAMPUSMATE.cmd --reset-admin
```

## What is included

- Midnight black, pure white and lime green website.
- Student sign-up/login, chatbot, source viewer, noticeboard and tickets.
- Admin login, PDF/FAQ upload, publishing, replacement and ticket workspace.
- 29 reviewed JSCOE FAQs covering admissions, fees and calendar information.
- Subject-wise exam timetable editor for your own dates, times and venues.
- Subject names, aliases and semester wording such as maths/M1, Physics/EP,
  Chemistry, C programming, sem1 and first semester.
- Explicitly labelled demo exam dates for testing all FY subject names. These
  fictional dates are separate from college notices and admin-entered dates.

## Add your exam dates

Open **Admin Login → Exam timetable**, enter your subjects and dates, then click
**Save and publish timetable**. Students can ask for one subject or all dates.
To test the bundled fictional examples, click **Try demo exam dates** in chat.

The college calendar provides an exam window, not an exact day for every paper.
The bot explains that distinction when no subject-wise timetable is available.
It does not turn a calendar start date into an invented Mathematics paper date.

## If the website was already running

Close old CampusMate server windows before starting this final edition. If port
5173 is occupied, the launcher asks you to close the old server and run again.

This ZIP is a complete fresh project. Existing data stays in your old folder.
If you want to retain it, stop the old servers and copy your own `backend/.env`,
`backend/campusmate.db` and `backend/storage` into the same locations in this
project before the first run. Do not copy an old virtual environment.

## Upload the code to GitHub

To publish the source to your `ashokbon8/campusmate` repository, run this from
the same VS Code terminal:

```powershell
.\UPLOAD_TO_GITHUB.cmd
```

Complete Git's sign-in in your own browser if prompted. The command uses an
explicit list of release files, excludes private settings and local data, and
prints **Upload verified** only after checking the remote commit. It needs
Git and Python; it does not require the website's packages to be installed.
Your local project files are preserved. Read [PUBLISH_ONLINE.md](PUBLISH_ONLINE.md)
for the next hosting step.

## Editing the source later

All frontend and backend source is included. Backend changes take effect after
restarting the Run command. To change the React website, install Node.js and
run these commands from the project folder after editing:

```powershell
cd frontend
npm.cmd ci
npm.cmd run build
```

Then restart CampusMate. Developers may still use the separate Vite/FastAPI
commands documented in `README.md`; normal use of the final ZIP needs only the
Run command above.

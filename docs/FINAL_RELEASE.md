# CampusMate Final

The final release ZIP is the full project with all changes already included.
It contains a prebuilt React website plus its source, the Python API, the
reviewed JSCOE FAQs, subject aliases, demo dates, exam timetable editor, admin
setup and Windows launcher. It is not an update patch.

Extract it, open that extracted folder in VS Code, and run:

```powershell
.\RUN_CAMPUSMATE.cmd
```

Python 3.12 or 3.11 is required. The launcher installs the Python dependencies,
sets up a private admin account once and runs both the website and API on
http://localhost:5173. It opens the browser after the API is ready. Node.js and
separate backend/frontend terminals are not required for normal use of this ZIP.

`Open_CampusMate.code-workspace` also provides a Run CampusMate task whose
working directory is fixed to the project folder. All files are directly at
the ZIP root, preventing the previous extra-folder terminal problem.

Admin credentials and a random signing secret are created locally. No user
password, local database or dependency environment is included in the release.
Existing configurations are retained when running inside an existing project.
A fresh extracted folder uses its own local configuration and database.

## Validation

205 Python tests and 55 frontend tests passed, and the production frontend
build succeeded. The following additional release checks apply to the bundled
download:

- The combined server is checked with FastAPI's test client for built HTML,
  the `/api` health/category/chat routes and the demo timetable source page.
- First-run checks cover new setup, preserving an existing administrator and
  explicit administrator reset.
- The exam/admission/authentication/source regression suite and frontend tests
  are retained in the full source.
- The final ZIP is extracted into a clean temporary folder and tested there,
  including admin login, exact custom exam dates and separate demo dates.
- The production React build is included and validated against its source.
- Cloud checks cover persistent-database and private-credential requirements,
  retaining original PDFs, and re-indexing after temporary files disappear.

The Windows batch launcher and an interactive browser review cannot be run on
this Linux execution host. The Python server, configuration, routes, source
rendering, frontend build and tests are checked here.

## Hackathon and online release

The newest complete archive is `CampusMate_GitHub_Ready.zip`. It also contains
the verified `frontend/dist` in the Git source and `UPLOAD_TO_GITHUB.cmd` for
upload through the user's own Git sign-in. The uploader is checked against a
local bare repository; actual GitHub write access from this session was denied.

`CampusMate_Hackathon_Ready.zip` is the complete later release with local startup
plus `Dockerfile`, `render.yaml` and `PUBLISH_ONLINE.md`. It is ready for a GitHub
commit and cloud deployment. No external GitHub push or live deployment is
claimed until the corresponding connected account confirms it. The new cloud
Docker image was not built on this host because Docker is unavailable.

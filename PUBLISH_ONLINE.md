# Submit CampusMate to the hackathon

## What to submit

**Project name:** CampusMate — Smart Student Helpdesk Chatbot.

**GitHub repository:** https://github.com/ashokbon8/campusmate

That repository must contain this latest source, not just an old version or a
ZIP attachment. Set the branch with the final code as the default branch, or
merge it into the default branch before submitting the repository URL. The
hackathon may require public visibility; follow its actual submission rules.

**Live website:** copy the real HTTPS address returned after deployment into
the GitHub repository's About → Website field. Also add it near the top of the
README. The target name is `campusmate-jscoe`; availability is decided by the
host. An example address would be `https://campusmate-jscoe.onrender.com`.
This example is not a confirmed live deployment.

## Put this final code on GitHub

From the complete ZIP, open the extracted folder in VS Code and run:

```powershell
.\UPLOAD_TO_GITHUB.cmd
```

Git may open your own browser for GitHub sign-in. Choose `ashokbon8`. This
uploads the explicit release file list to `ashokbon8/campusmate`, preserves the
existing remote history, and verifies the resulting commit. Private local
settings, databases, uploads and dependency folders are excluded. The helper
uses a temporary checkout and leaves your local project untouched. Git must
be installed; the uploader needs only Python's standard library.

The GitHub app connected to this chat did not grant code-write access. This
local command uses your own Git sign-in to complete the authorized upload.
After it says **Upload verified**, send the repository link back so the online
deployment can continue.

### Manual source-control option

The easiest way from VS Code:

1. Extract the complete **CampusMate_GitHub_Ready.zip** into a new folder.
2. Open that folder in VS Code. Use **Source Control → Initialize Repository**
   if the downloaded folder does not already have Git history.
3. Stage the source files, enter a commit message such as `Prepare CampusMate
   hackathon release`, and commit. The supplied `.gitignore` excludes private
   configuration, databases, uploads, installed packages and build output.
4. Publish to your GitHub account `ashokbon8` with the repository name
   `campusmate`. If the repository already exists, push a new branch and merge
   it using a pull request. Do not force-push over existing repository history.
5. Open the repository on GitHub and confirm that README.md, backend, frontend,
   Dockerfile and render.yaml are visible. Do not upload the ZIP as the only
   project file. Never commit your local `backend/.env` or passwords.

Submit the URL of the repository that actually contains these final files.
If you use a new repository, update any old repository links in this README.

## Publish the complete website on Render

The included `render.yaml` builds React and Python into one service and creates
a PostgreSQL database. Login, saved students, tickets, custom exam timetables
and original newly uploaded PDFs are stored in that database. There is no
second frontend hostname or API URL to configure.

1. Sign in to https://dashboard.render.com and connect your GitHub account.
2. Choose **New → Blueprint**, then select the repository and branch containing
   this final source. Leave the Blueprint path as `render.yaml`.
3. Enter `SEED_ADMIN_EMAIL` and `SEED_ADMIN_PASSWORD` when prompted. Choose a
   password of at least 12 characters. Enter credentials only in Render's
   private environment settings. `SECRET_KEY` is generated automatically.
4. Check the resource summary. The supplied Blueprint selects **Free** for both
   the web service and database. Click **Deploy Blueprint**.
5. Wait for the service to become Live. Open its actual HTTPS URL, create a
   student account, and test a college FAQ and a demo exam question. Sign in as
   admin and publish your real timetable. The browser URL is now the cloud URL;
   local `localhost:5173` remains available for development on your laptop.
6. Put that confirmed URL in GitHub's About → Website field and README. Submit
   the GitHub repository URL to the hackathon. Submit the website separately
   only if its form has a live-demo field.

The public name can be adjusted in Render's service settings if your preferred
name is available. You do not need to buy a domain for a named HTTPS demo URL.
Connecting a domain you own is optional and uses the host's custom-domain setup.

## Free-plan limits that affect judging

Checked against Render's official documentation on 13 November 2026:

- Free web services sleep after 15 minutes without traffic and usually take
  about a minute to start on the next visit. Open the website before presenting.
- Free Render PostgreSQL expires **30 days after creation**, has 1 GB of
  storage, and has no included backups. Use a paid database before expiry, or
  move DATABASE_URL to another persistent PostgreSQL host, if judging is later.
- Only one free Render PostgreSQL database may be active in a workspace. Reuse
  an existing database by setting DATABASE_URL manually if the Blueprint cannot
  create another one.
- Local server files are temporary. This version stores original PDFs uploaded
  through the admin workspace in the database as well as a temporary local
  cache. Uploaded PDFs from an older version must be uploaded again to gain
  that protection. External official college sources still open their original
  college URLs.
- Your local laptop database is not automatically copied to the online site.
  The online site imports the included 29 college FAQs; recreate any custom
  exam rows in its admin timetable editor.

Official references:
https://render.com/docs/infrastructure-as-code
https://render.com/docs/blueprint-spec
https://render.com/docs/free

## Quick judge walkthrough

1. Open the public website in a private browser window; create a student account.
2. Ask `Which documents do I need for admission?` and open its official source.
3. Ask a Semester 1 exam-date question. Use **Try demo exam dates** to demonstrate
   fictional dates, or publish your own schedule through **Admin Login → Exam
   timetable**. Demo dates remain clearly labelled and separate from real data.
4. Show the noticeboard and the helpdesk ticket workflow.
5. Show admin publishing or a timetable revision from your own account. Keep
   admin credentials private; judges can register as students themselves.

The application uses deterministic retrieval and answer rules by default, so
the demo does not require a paid AI API. Do not describe sample dates as college
announcements or claim measured results that the project has not verified.

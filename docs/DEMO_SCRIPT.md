# 90-second demonstration script

A planned demo sequence that exercises the core CampusMate behaviours. This is
a **plan**, not evidence that the application has passed these checks — the
measured test results are in [TESTING.md](TESTING.md).

All data used here is synthetic sample data ([DEMO_DATA.md](DEMO_DATA.md)).

## Before you start

```bash
# backend
cd backend && uvicorn app.main:app --reload --port 8000
# frontend
cd frontend && npm run dev
```

Open the frontend. The public home intro appears first; click **Create account**
to register a student (or **Sign in** if you already have one). Keep a second tab
for the admin workspace, where you sign in with the private staff credentials
supplied through your environment (`SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD`) —
they are not shown in the UI.

---

## 0–20s — Routine question with a source

1. On the home intro, click **Create account** and register a student.
2. On the chatbot page, type or click: *"Which documents do I need?"*
3. The answer returns as `answered` with a source card.
4. Click the source card to open the sample notice PDF at the cited page.

**Shows:** a routine answer grounded in an approved document, with an
inspectable source (name, page, date, version, status).

---

## 20–40s — Clarification before answering

1. Type: *"When is my exam?"* (leave the context fields empty).
2. CampusMate returns `needs_context` and asks which programme, semester and
   subject.
3. Fill Programme `BSc CS`, Semester `1`, Subject `Mathematics` (or just
   restate the question) and send.
4. CampusMate returns `answered`: the sample examination date, time and room,
   citing the sample notice v2, page 1.

**Shows:** CampusMate asks for missing context instead of guessing.

---

## 40–65s — Publish a replacement notice

1. Switch to the **Admin** workspace and log in.
2. Upload a revised examination notice (PDF or FAQ), set
   `replaces_document_id` to the current notice, and give it the new details.
3. Review the extracted text, then **Publish**.
4. Back in the chat, ask *"When is my Mathematics exam?"* again.
5. CampusMate now answers from the new version and labels the previous one as
   `replaced`.

**Shows:** the document version workflow — upload, validate, re-index, activate,
retire the old notice — and that the chatbot uses the updated notice.

---

## 65–90s — Unsupported question escalates

1. Type a question with no approved notice, e.g. *"What is the cafeteria menu on
   Friday?"*
2. CampusMate returns `escalated`: it explains that the approved information
   cannot answer the question and offers a helpdesk ticket.
3. Click **Raise a helpdesk ticket**; the ticket form is prefilled with the
   category and question.

**Shows:** CampusMate does not invent an answer; it escalates and provides a
clear next step.

---

## Notes for the presenter

- Say plainly that the data is synthetic sample data.
- Point out the source card fields each time an answer is returned.
- Mention that the validation numbers are measured on this demo build with
  stub models, and are separate from the presentation's proposed targets.

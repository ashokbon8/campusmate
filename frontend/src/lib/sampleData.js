/**
 * Synthetic demonstration content from the presentation.
 *
 * IMPORTANT: every item here is clearly-labelled SAMPLE data. It is never real
 * college information. The example conversation mirrors the PPTX slide showing
 * that CampusMate asks a clarifying question before answering.
 */

export const EXAMPLE_CONVERSATION = {
  title: "Example conversation using JSCOE sources",
  note: "This example uses the posted JSCOE 2026–27 fee table, checked on 13 November 2026.",
  turns: [
    { role: "student", text: "What are the fees?" },
    {
      role: "assistant",
      state: "needs_context",
      text: "Which programme are you asking about?",
    },
    { role: "student", text: "B.Tech, OPEN category." },
    {
      role: "assistant",
      state: "answered",
      text: "The posted 2026–27 B.E fee table lists an OPEN-category total of Rs 1,20,000. Confirm your final payable amount with accounts.",
      citation: {
        document_title: "JSCOE Fee Structure 2026–27",
        page: 1,
        checked_on: "13 November 2026",
        version: 1,
      },
    },
  ],
};

export const PROBLEMS = [
  {
    id: "scattered",
    title: "Scattered notices",
    body: "Students search multiple places to find useful information.",
  },
  {
    id: "context",
    title: "Missing context",
    body: "Fees and timetables depend on programme, semester, and date.",
  },
  {
    id: "repeated",
    title: "Repeated office queries",
    body: "Staff repeatedly answer common questions while unusual cases wait.",
  },
];

export const WORKFLOW = [
  {
    step: 1,
    title: "Ask a question in everyday language",
    body: "Type your question the way you would say it. Add your programme and semester when you can.",
  },
  {
    step: 2,
    title: "Read an answer with its official source",
    body: "Every answer shows the notice it came from, the exact page, the publication date and the version.",
  },
  {
    step: 3,
    title: "Clarify, or create a helpdesk ticket",
    body: "If details are missing CampusMate asks for them. If nothing supports the answer, raise a ticket instead of guessing.",
  },
];

export const TOPICS = [
  {
    id: "admissions",
    name: "Admissions",
    example: "Which documents do I need?",
    context: "Programme and entry route.",
    description: "Entry requirements, document checklists and eligibility.",
  },
  {
    id: "fees",
    name: "Fees",
    example: "What are the B.Tech fees for 2026-27?",
    context: "Programme and academic year.",
    description:
      "Posted programme/category fee tables. Private fee balances are not available here.",
  },
  {
    id: "examinations",
    name: "Examinations",
    example: "Where can I find examination notices?",
    context: "Semester and subject.",
    description: "Calendar exam windows and clearly dated examination sources.",
  },
  {
    id: "timetables",
    name: "Timetables",
    example: "Show the first year academic calendar",
    context: "Division, day, and time.",
    description: "First-year academic calendar, CCE dates and semester milestones.",
  },
  {
    id: "activities",
    name: "College activities",
    example: "How do I register for an event?",
    context: "Event and eligibility.",
    description: "Events, clubs, sports and how to register.",
  },
];

export const TICKET_STATUSES = [
  "open",
  "pending",
  "in_progress",
  "resolved",
  "closed",
];

export const STATUS_LABELS = {
  open: "Open",
  pending: "Pending",
  in_progress: "In progress",
  resolved: "Resolved",
  closed: "Closed",
};

export const PROPOSED_TARGETS = [
  { label: "Supported-answer accuracy", target: "90%+" },
  { label: "Citation coverage", target: "100% of factual answers" },
  { label: "Unsupported guesses", target: "Zero across the unsupported set" },
  { label: "p95 response time", target: "5s or less on the demo setup" },
];

/**
 * Measured results for THIS demo build with synthetic sample data.
 *
 * Produced by `python tests/run_validation.py` over the 50-question dataset.
 * These are real measurements of the offline demo, not the proposed targets,
 * and they do not represent performance on real college data.
 */
export const MEASURED_RESULTS = {
  runLabel: "50-question curated dataset · offline stub LLM · sample data",
  metrics: [
    { label: "Supported-answer accuracy", measured: "25/25 (100%)", target: "90%+" },
    { label: "Citation coverage", measured: "26/26 (100%)", target: "100%" },
    { label: "Unsupported guesses", measured: "0 of 10", target: "0" },
    { label: "Clarification rate", measured: "10/50 (20%)", target: "n/a" },
    { label: "Escalation rate", measured: "14/50 (28%)", target: "n/a" },
    { label: "p95 response time", measured: "8 ms (local)", target: "≤ 5s" },
  ],
  caveat:
    "Latency was measured locally with a deterministic stub model. A hosted model adds network time; re-run the harness against the target deployment before quoting it.",
};

export const TEST_DATASET = [
  { label: "Routine questions (5 per category)", count: 25 },
  { label: "Questions missing context", count: 10 },
  { label: "Outdated or conflicting notices", count: 5 },
  { label: "Unsupported questions", count: 10 },
];

export const ROADMAP = [
  "Hindi and Marathi support",
  "Opt-in deadline reminders (require student consent)",
  "Student portal integration (authentication + separate permission design)",
  "Staff review of unanswered topics",
];

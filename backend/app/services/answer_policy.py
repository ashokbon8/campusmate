"""Answer policy: category detection, context requirements and evidence checks.

This module encodes the rules that keep CampusMate from guessing:

1. Identify the category of a question.
2. Decide which context is required (programme / semester / subject / ...).
3. Ask for missing context instead of answering.
4. Only return an answer that is supported by retrieved evidence.
5. Escalate (offer a ticket) when nothing supports the question.
"""

from __future__ import annotations

import re

# Keyword sets used for lightweight category classification.
#
# STRONG keywords are the category's core nouns: a single match is enough to
# commit to that category. WEAK keywords are generic words that often appear in
# unrelated questions ("schedule", "marks", "timing"), so they only reinforce a
# category that a strong keyword already selected. Keeping the two apart stops
# questions like "what is the bus route timing?" from being mistaken for a
# timetable question.
STRONG_KEYWORDS: dict[str, list[str]] = {
    "Admissions": [
        "admission", "admissions", "enrolment", "enrollment", "entrance",
        "eligibility", "cutoff", "merit list", "document", "documents",
    ],
    "Fees": [
        "fee", "fees", "tuition", "instalment", "installment", "scholarship",
        "refund", "receipt",
    ],
    "Examinations": [
        "exam", "exams", "examination", "viva", "backlog", "re-exam",
        "hall ticket", "seat number", "answer sheet", "retest", "result",
    ],
    "Timetables": [
        "timetable", "time table", "lecture", "class", "classes", "lab",
        "semester schedule", "next class", "academic calendar", "calendar",
        "induction", "cce", "preparation leave", "open day",
    ],
    "College activities": [
        "event", "events", "activity", "activities", "club", "society", "fest",
        "festival", "sports", "workshop", "cultural", "nss", "ncc",
        "competition",
    ],
}

WEAK_KEYWORDS: dict[str, list[str]] = {
    "Admissions": ["apply", "application", "document", "documents", "submit"],
    "Fees": ["pay", "payment", "deadline", "balance", "due"],
    "Examinations": ["test", "paper", "marks", "result", "results", "date",
                     "timing"],
    "Timetables": ["schedule", "timing", "slot", "period", "room"],
    "College activities": ["register", "registration", "join", "sign up"],
}

# Ordered list of the five official categories.
CATEGORIES = list(STRONG_KEYWORDS.keys())

# Context a category needs before a specific answer can be given. Keys map to
# human-readable prompt fragments used to build the clarification question.
REQUIRED_CONTEXT: dict[str, list[str]] = {
    "Admissions": ["programme"],
    "Fees": ["programme", "academic_year"],
    "Examinations": ["programme", "semester", "subject"],
    "Timetables": ["programme", "semester"],
    "College activities": [],
}

CONTEXT_LABELS = {
    "programme": "your programme",
    "semester": "your semester",
    "subject": "the subject",
    "academic_year": "the academic year",
}


def _matches(keyword: str, text: str) -> bool:
    """Whole-word (or phrase) match, tolerant of simple plural/tense endings."""
    pattern = r"\b" + re.escape(keyword) + r"(?:s|es|ed|ing)?\b"
    return re.search(pattern, text) is not None


def detect_category(question: str) -> str | None:
    """Return the best-matching category, or ``None`` when nothing is confident.

    A category is only returned when at least one *strong* keyword matches, so
    generic words alone never commit the system to a category.
    """
    q = question.lower()
    # A document *about fees/exams* belongs to that topic, not Admissions.
    if re.search(r'\b(fee|fees|tuition|refund|scholarship)\b', q):
        return 'Fees'
    if re.search(r'\bacademic calendar\b|\bcce\b|\binduction\b', q):
        return 'Timetables'
    if re.search(r'\bproject competition\b', q):
        return 'Timetables'
    strong_scores: dict[str, int] = {}
    weak_scores: dict[str, int] = {}
    for category in CATEGORIES:
        strong = sum(1 for kw in STRONG_KEYWORDS[category] if _matches(kw, q))
        weak = sum(1 for kw in WEAK_KEYWORDS[category] if _matches(kw, q))
        if strong:
            strong_scores[category] = strong
        if weak:
            weak_scores[category] = weak
    if not strong_scores:
        return None
    return max(
        strong_scores,
        key=lambda c: (strong_scores[c], weak_scores.get(c, 0), -CATEGORIES.index(c)),
    )


def category_score(question: str) -> dict[str, int]:
    """Expose per-category hit counts (used for diagnostics and tests)."""
    q = question.lower()
    return {
        category: sum(1 for kw in STRONG_KEYWORDS[category] if _matches(kw, q))
        for category in CATEGORIES
    }


def missing_context(
    category: str | None, context: dict[str, str | None]
) -> list[str]:
    if not category:
        return []
    required = REQUIRED_CONTEXT.get(category, [])
    return [field for field in required if not (context.get(field) or "").strip()]


def build_clarification(category: str | None, missing: list[str]) -> str:
    if not missing:
        return "Could you share a little more detail so I can find the right notice?"
    labels = [CONTEXT_LABELS.get(field, field) for field in missing]
    if len(labels) == 1:
        wanted = labels[0]
    elif len(labels) == 2:
        wanted = f"{labels[0]} and {labels[1]}"
    else:
        wanted = ", ".join(labels[:-1]) + f", and {labels[-1]}"
    if category:
        return (
            f"Could you tell me {wanted}? I need that to find the correct "
            f"{category.lower()} notice."
        )
    return f"Could you tell me {wanted}?"


# ---------------------------------------------------------------------------
# Evidence validation
# ---------------------------------------------------------------------------
_NUMBER_RE = re.compile(r"\b\d{1,4}(?:[:.]\d{2})?\b")
_MONTH_RE = re.compile(
    r"\b(january|february|march|april|may|june|july|august|september|october|"
    r"november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\b",
    re.IGNORECASE,
)


def extract_checkable_tokens(text: str) -> set[str]:
    """Pull out numbers, times and month names that must be evidence-backed."""
    tokens = set(_NUMBER_RE.findall(text.lower()))
    tokens |= {m.lower() for m in _MONTH_RE.findall(text)}
    return tokens


def answer_supported_by_evidence(answer: str, evidence: list[str]) -> bool:
    """Every date/number in the answer must appear somewhere in the evidence.

    This is a conservative, explainable guard: it cannot prove correctness, but
    it reliably blocks the most damaging failure mode (an invented date, fee or
    exam time). It is not a claim of "zero hallucinations".
    """
    if not evidence:
        return False
    haystack = " ".join(evidence).lower()
    haystack_tokens = extract_checkable_tokens(haystack)
    for token in extract_checkable_tokens(answer):
        if token not in haystack_tokens and token not in haystack:
            return False
    return True

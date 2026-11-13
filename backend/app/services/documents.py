"""Document ingestion: text extraction, chunking and indexing.

Retrieved document content is treated as untrusted data. ``sanitize_passage``
strips common prompt-injection patterns before text is stored or sent to the
language model.
"""

from __future__ import annotations

import hashlib
import io
import re

from pypdf import PdfReader
from sqlalchemy.orm import Session

from ..models import Document, Passage
from .embeddings import get_embedder

# Patterns that often appear in prompt-injection attempts inside documents.
_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"disregard (all )?(previous|prior|above)",
    r"system prompt",
    r"you are now",
    r"act as (an?|the) ",
    r"assistant:\s",
    r"developer mode",
]
_INJECTION_RE = re.compile("|".join(_INJECTION_PATTERNS), re.IGNORECASE)


def sanitize_passage(text: str) -> str:
    """Neutralise prompt-injection content and normalise whitespace.

    Horizontal whitespace is collapsed, but line breaks are preserved so that
    notices keep their row structure (a heading stays separate from the fact
    beneath it, which keeps generated answers free of stray headers).
    """
    text = _INJECTION_RE.sub("[removed]", text)
    text = re.sub(r"[^\S\n]+", " ", text)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def extract_pdf_pages(data: bytes) -> list[tuple[int, str]]:
    """Return ``[(page_number, text), ...]`` (1-indexed)."""
    reader = PdfReader(io.BytesIO(data))
    pages: list[tuple[int, str]] = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:  # pragma: no cover - malformed PDFs
            text = ""
        pages.append((i, text))
    return pages


def extract_text_pages(text: str) -> list[tuple[int, str]]:
    """Treat a plain FAQ body as a single page."""
    return [(1, text)]


def chunk_text(text: str, max_chars: int = 600, overlap: int = 80) -> list[str]:
    """Split text into overlapping chunks on sentence boundaries where possible."""
    text = text.strip()
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_chars:
            current = f"{current} {sentence}".strip()
        else:
            if current:
                chunks.append(current)
            # Start new chunk, carrying a small overlap from the previous one.
            tail = current[-overlap:] if current else ""
            current = f"{tail} {sentence}".strip() if tail else sentence
            if len(current) > max_chars * 2:
                # Guard against a single very long sentence.
                for start in range(0, len(current), max_chars):
                    chunks.append(current[start : start + max_chars])
                current = ""
    if current:
        chunks.append(current)
    return [c for c in (chunk.strip() for chunk in chunks) if c]


def index_document(db: Session, document: Document, pages: list[tuple[int, str]]) -> int:
    """Extract, sanitise, embed and store passages for a document.

    Existing passages are replaced so this is safe to call again to re-index.
    """
    embedder = get_embedder()

    # Clear any previous passages (re-indexing).
    for passage in list(document.passages):
        db.delete(passage)
    db.flush()

    ordinal = 0
    texts: list[str] = []
    metas: list[tuple[int, str]] = []
    for page_number, page_text in pages:
        # A reviewed FAQ is one answer: retain all checklist/table rows together.
        cleaned = sanitize_passage(page_text)
        chunks = ([cleaned] if cleaned else []) if document.doc_uid.startswith("jscoe-") or document.doc_type == 'exam' else chunk_text(cleaned)
        for chunk in chunks:
            texts.append(chunk)
            metas.append((page_number, chunk))

    if not texts:
        return 0

    vectors = embedder.embed(texts)
    for (page_number, chunk), vector in zip(metas, vectors):
        document.passages.append(
            Passage(
                page_number=page_number,
                ordinal=ordinal,
                content=chunk,
                embedding=vector,
            )
        )
        ordinal += 1
    document.content_hash = hashlib.sha256("\n".join(texts).encode()).hexdigest()
    db.flush()
    return len(texts)

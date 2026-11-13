"""Embedding model adapter.

Two implementations are provided behind one interface so the embedding model can
be swapped without redesigning the application:

* ``HashingEmbedder``  - deterministic, dependency-free, offline. Used by default
  so the demo and the test suite never require an API key.
* ``OpenAIEmbedder``   - calls a hosted embeddings endpoint.

Selected via ``EMBEDDING_PROVIDER`` (``hashing`` | ``openai``).
"""

from __future__ import annotations

import hashlib
import math
import re
from abc import ABC, abstractmethod

import httpx

from ..config import settings

_TOKEN_RE = re.compile(r"[a-z0-9]+")


class Embedder(ABC):
    dim: int

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class HashingEmbedder(Embedder):
    """Hashing trick (a.k.a. the "hashing" vectoriser) with sub-linear term
    weighting. Deterministic and offline, which keeps retrieval testable."""

    def __init__(self, dim: int | None = None) -> None:
        self.dim = dim or settings.embedding_dim

    def _vector(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        tokens = _tokenize(text)
        if not tokens:
            return vec
        # Add unigrams and bigrams for a little word-order sensitivity.
        grams = list(tokens)
        grams += [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]
        counts: dict[str, int] = {}
        for g in grams:
            counts[g] = counts.get(g, 0) + 1
        for gram, count in counts.items():
            h = hashlib.blake2b(gram.encode("utf-8"), digest_size=8).digest()
            idx = int.from_bytes(h[:4], "big") % self.dim
            sign = 1.0 if h[4] % 2 == 0 else -1.0
            vec[idx] += sign * (1.0 + math.log(count))
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]


class OpenAIEmbedder(Embedder):  # pragma: no cover - requires network
    def __init__(self) -> None:
        self.dim = settings.embedding_dim
        self._client = httpx.Client(
            base_url=settings.embedding_base_url,
            headers={"Authorization": f"Bearer {settings.embedding_api_key}"},
            timeout=30,
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        resp = self._client.post(
            "/embeddings", json={"model": settings.embedding_model, "input": texts}
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        return [item["embedding"] for item in data]


def get_embedder() -> Embedder:
    if settings.embedding_provider == "openai" and settings.embedding_api_key:
        return OpenAIEmbedder()
    return HashingEmbedder()


def cosine(a, b) -> float:
    if a is None or b is None:
        return 0.0
    # pgvector returns numpy arrays; SQLite returns JSON lists. Normalise both.
    a = [float(x) for x in a]
    b = [float(x) for x in b]
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

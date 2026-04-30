from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    type: str
    tier: int
    trust_score: float
    categories: tuple[str, ...]
    max_items: int
    url: str | None = None
    query: str | None = None
    enabled: bool = True


@dataclass(frozen=True)
class CollectedItem:
    title: str
    summary: str
    url: str
    published_at: datetime
    source: Source
    authors: tuple[str, ...] = ()


@dataclass(frozen=True)
class ClassifiedItem(CollectedItem):
    category: str = "Other"
    matched_keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class RankedItem(ClassifiedItem):
    score: int = 0
    signals: tuple[str, ...] = ()


@dataclass(frozen=True)
class Digest:
    subject: str
    body: str

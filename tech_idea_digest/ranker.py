from __future__ import annotations

from datetime import datetime, timezone

from tech_idea_digest.classifier import classify_item
from tech_idea_digest.models import ClassifiedItem, CollectedItem, RankedItem

IMPACT_KEYWORDS = (
    "benchmark",
    "benchmarks",
    "production",
    "scalable",
    "scale",
    "paper",
    "result",
    "results",
    "evaluation",
    "open source",
)


def rank_items(
    items: list[CollectedItem | ClassifiedItem],
    *,
    max_items: int = 20,
    max_per_category: int = 4,
    now: datetime | None = None,
) -> list[RankedItem]:
    reference_time = now or datetime.now(timezone.utc)
    classified = [item if isinstance(item, ClassifiedItem) else classify_item(item) for item in items]
    eligible = [_rank_item(item, reference_time) for item in classified if _passes_quality_gate(item)]
    ranked = sorted(eligible, key=lambda item: item.score, reverse=True)
    return _limit_per_category(ranked, max_items=max_items, max_per_category=max_per_category)


def _passes_quality_gate(item: ClassifiedItem) -> bool:
    if item.source.tier >= 3:
        return False
    if not item.title.strip() or not item.summary.strip() or not item.url.strip():
        return False
    return item.source.trust_score >= 0.5


def _rank_item(item: ClassifiedItem, now: datetime) -> RankedItem:
    source_points = item.source.trust_score * 30
    recency_points, recency_signal = _score_recency(item.published_at, now)
    relevance_points = min(25, 10 + len(item.matched_keywords) * 5)
    impact_points = _score_impact(item)

    score = int(round(min(100, source_points + recency_points + relevance_points + impact_points)))
    signals = ["source-quality"]
    if recency_signal:
        signals.append(recency_signal)
    if item.matched_keywords:
        signals.append("relevance")
    if impact_points:
        signals.append("impact-signal")

    return RankedItem(
        title=item.title,
        summary=item.summary,
        url=item.url,
        published_at=item.published_at,
        source=item.source,
        authors=item.authors,
        category=item.category,
        matched_keywords=item.matched_keywords,
        score=score,
        signals=tuple(signals),
    )


def _limit_per_category(
    items: list[RankedItem],
    *,
    max_items: int,
    max_per_category: int,
) -> list[RankedItem]:
    selected: list[RankedItem] = []
    category_counts: dict[str, int] = {}
    for item in items:
        if len(selected) >= max_items:
            break
        count = category_counts.get(item.category, 0)
        if count >= max_per_category:
            continue
        selected.append(item)
        category_counts[item.category] = count + 1
    return selected


def _score_recency(published_at: datetime, now: datetime) -> tuple[int, str | None]:
    age = now - _ensure_aware(published_at)
    days = age.total_seconds() / 86400
    if days <= 2:
        return 20, "recent"
    if days <= 7:
        return 12, "this-week"
    if days <= 30:
        return 5, "this-month"
    return 0, None


def _score_impact(item: ClassifiedItem) -> int:
    text = f"{item.title} {item.summary}".lower()
    matches = sum(1 for keyword in IMPACT_KEYWORDS if keyword in text)
    return min(15, matches * 5)


def _ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)

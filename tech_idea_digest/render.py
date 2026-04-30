from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from tech_idea_digest.models import Digest, RankedItem


def render_digest(items: list[RankedItem], *, generated_at: datetime | None = None) -> Digest:
    timestamp = generated_at or datetime.now(timezone.utc)
    subject = f"Daily Technology Ideas Digest - {timestamp.date().isoformat()}"
    lines = [subject, "", "Top Signals"]

    if not items:
        lines.extend(["", "No high-quality technology signals passed today's filters."])
        return Digest(subject=subject, body="\n".join(lines))

    for item in items[:5]:
        lines.extend(_render_item(item))

    lines.extend(["", "By Category"])
    grouped: dict[str, list[RankedItem]] = defaultdict(list)
    for item in items:
        grouped[item.category].append(item)

    for category in sorted(grouped):
        lines.extend(["", category])
        for item in grouped[category]:
            lines.append(f"- {item.score}/100 - {item.title}")
            lines.append(f"  Link: {item.url}")

    return Digest(subject=subject, body="\n".join(lines))


def _render_item(item: RankedItem) -> list[str]:
    why = _why_it_matters(item)
    signals = ", ".join(item.signals)
    return [
        "",
        f"Score: {item.score}/100",
        f"Category: {item.category}",
        f"Title: {item.title}",
        f"Summary: {_one_line(item.summary)}",
        f"Why it matters: {why}",
        f"Source: {item.source.name} (Tier {item.source.tier})",
        f"Signals: {signals}",
        f"Link: {item.url}",
    ]


def _why_it_matters(item: RankedItem) -> str:
    if item.matched_keywords:
        keywords = ", ".join(item.matched_keywords[:3])
        return f"It matches high-value technology signals around {keywords} from a curated source."
    return "It passed the source quality and recency gates for the daily technology scan."


def _one_line(value: str, *, limit: int = 220) -> str:
    compact = " ".join(value.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 3].rstrip()}..."

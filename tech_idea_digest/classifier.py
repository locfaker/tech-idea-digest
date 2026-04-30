from __future__ import annotations

import re

from tech_idea_digest.models import ClassifiedItem, CollectedItem

CATEGORY_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Agents & Automation",
        ("agent", "agents", "agentic", "automation", "autonomous", "workflow", "tool use", "memory"),
    ),
    (
        "AI/ML",
        ("ai", "machine learning", "deep learning", "llm", "language model", "rag", "transformer"),
    ),
    (
        "Security",
        ("security", "vulnerability", "malware", "isolation", "zero trust", "exploit", "privacy"),
    ),
    (
        "Cloud & DevOps",
        ("cloud", "kubernetes", "container", "distributed", "infrastructure", "runtime", "deployment"),
    ),
    (
        "Data",
        ("database", "data", "analytics", "replication", "warehouse", "consistency", "streaming"),
    ),
    (
        "Web & Mobile",
        ("frontend", "backend", "web", "mobile", "rendering", "api", "typescript", "javascript"),
    ),
    (
        "Hardware & Robotics",
        ("robot", "robotics", "sensor", "hardware", "edge", "iot", "chip"),
    ),
    (
        "Blockchain",
        ("blockchain", "web3", "smart contract", "crypto", "zk", "zero knowledge"),
    ),
)


def classify_item(item: CollectedItem) -> ClassifiedItem:
    text = f"{item.title} {item.summary}".lower()
    best_category = item.source.categories[0] if item.source.categories else "Other"
    best_matches: tuple[str, ...] = ()

    for category, keywords in CATEGORY_KEYWORDS:
        matches = tuple(keyword for keyword in keywords if _matches_keyword(text, keyword))
        if len(matches) > len(best_matches):
            best_category = category
            best_matches = matches

    return ClassifiedItem(
        title=item.title,
        summary=item.summary,
        url=item.url,
        published_at=item.published_at,
        source=item.source,
        authors=item.authors,
        category=best_category,
        matched_keywords=best_matches,
    )


def _matches_keyword(text: str, keyword: str) -> bool:
    escaped = re.escape(keyword.lower())
    return re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text) is not None

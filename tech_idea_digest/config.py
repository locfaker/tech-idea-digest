from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tech_idea_digest.models import Source

SUPPORTED_SOURCE_TYPES = {"arxiv", "rss"}
MIN_ENABLED_TRUST_SCORE = 0.5


def load_sources(path: str | Path) -> list[Source]:
    config_path = Path(path)
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    raw_sources = data.get("sources")
    if not isinstance(raw_sources, list):
        raise ValueError("sources.yaml must contain a 'sources' list")

    sources = [_parse_source(raw) for raw in raw_sources]
    return [source for source in sources if source.enabled]


def _parse_source(raw: Any) -> Source:
    if not isinstance(raw, dict):
        raise ValueError("Each source must be an object")

    source_id = _required_str(raw, "id")
    source_type = _required_str(raw, "type")
    if source_type not in SUPPORTED_SOURCE_TYPES:
        raise ValueError(f"Unsupported source type for {source_id}: {source_type}")

    tier = int(raw.get("tier", 3))
    if tier < 1 or tier > 3:
        raise ValueError(f"Invalid tier for {source_id}: {tier}")

    trust_score = float(raw.get("trust_score", 0))
    enabled = bool(raw.get("enabled", True))
    if enabled and trust_score < MIN_ENABLED_TRUST_SCORE:
        raise ValueError(f"Enabled source {source_id} has trust_score below {MIN_ENABLED_TRUST_SCORE}")

    categories = raw.get("categories")
    if not isinstance(categories, list) or not all(isinstance(item, str) for item in categories):
        raise ValueError(f"Source {source_id} must define categories as a string list")

    max_items = int(raw.get("max_items", 10))
    if max_items < 1:
        raise ValueError(f"Source {source_id} max_items must be positive")

    url = raw.get("url")
    query = raw.get("query")
    if source_type == "rss" and not isinstance(url, str):
        raise ValueError(f"RSS source {source_id} requires url")
    if source_type == "arxiv" and not isinstance(query, str):
        raise ValueError(f"arXiv source {source_id} requires query")

    return Source(
        id=source_id,
        name=_required_str(raw, "name"),
        type=source_type,
        tier=tier,
        trust_score=trust_score,
        enabled=enabled,
        categories=tuple(categories),
        max_items=max_items,
        url=url,
        query=query,
    )


def _required_str(raw: dict[str, Any], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Source requires non-empty {key}")
    return value.strip()

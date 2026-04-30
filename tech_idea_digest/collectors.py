from __future__ import annotations

import ssl
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Callable
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from xml.etree import ElementTree

import certifi
import feedparser

from tech_idea_digest.models import CollectedItem, Source

ARXIV_API_URL = "https://export.arxiv.org/api/query"
USER_AGENT = "tech-idea-digest/0.1 (+https://github.com/)"


def collect_all(
    sources: list[Source],
    *,
    on_error: Callable[[tuple[str, str]], None] | None = None,
) -> list[CollectedItem]:
    nested = tuple(_collect_source_safely(source, on_error) for source in sources)
    return _dedupe(tuple(item for group in nested for item in group))


def collect_source(source: Source) -> list[CollectedItem]:
    if source.type == "rss":
        if source.url is None:
            raise ValueError(f"RSS source {source.id} has no url")
        return parse_rss_feed(source, _fetch_text(source.url))
    if source.type == "arxiv":
        if source.query is None:
            raise ValueError(f"arXiv source {source.id} has no query")
        url = _arxiv_query_url(source.query, source.max_items)
        return parse_arxiv_feed(source, _fetch_text(url))
    raise ValueError(f"Unsupported source type: {source.type}")


def _collect_source_safely(
    source: Source,
    on_error: Callable[[tuple[str, str]], None] | None,
) -> list[CollectedItem]:
    try:
        return collect_source(source)
    except Exception as exc:
        if on_error is not None:
            on_error((source.id, str(exc)))
        return []


def parse_rss_feed(source: Source, content: str) -> list[CollectedItem]:
    parsed = feedparser.parse(content)
    return [
        CollectedItem(
            title=_clean(entry.get("title", "")),
            summary=_clean(entry.get("summary", "") or entry.get("description", "")),
            url=_clean(entry.get("link", "")),
            published_at=_feed_datetime(entry),
            source=source,
            authors=_entry_authors(entry),
        )
        for entry in parsed.entries[: source.max_items]
        if _clean(entry.get("title", "")) and _clean(entry.get("link", ""))
    ]


def parse_arxiv_feed(source: Source, content: str) -> list[CollectedItem]:
    root = ElementTree.fromstring(content)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", namespace)
    return [
        CollectedItem(
            title=_clean(_text(entry, "atom:title", namespace)),
            summary=_clean(_text(entry, "atom:summary", namespace)),
            url=_clean(_text(entry, "atom:id", namespace)),
            published_at=_iso_datetime(_text(entry, "atom:published", namespace)),
            source=source,
            authors=tuple(
                _clean(author.findtext("atom:name", default="", namespaces=namespace))
                for author in entry.findall("atom:author", namespace)
                if _clean(author.findtext("atom:name", default="", namespaces=namespace))
            ),
        )
        for entry in entries[: source.max_items]
        if _clean(_text(entry, "atom:title", namespace)) and _clean(_text(entry, "atom:id", namespace))
    ]


def _fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    context = ssl.create_default_context(cafile=certifi.where())
    with urlopen(request, timeout=30, context=context) as response:
        return response.read().decode("utf-8", errors="replace")


def _arxiv_query_url(query: str, max_items: int) -> str:
    encoded = quote_plus(query)
    return (
        f"{ARXIV_API_URL}?search_query={encoded}"
        f"&sortBy=submittedDate&sortOrder=descending&max_results={max_items}"
    )


def _text(entry: ElementTree.Element, path: str, namespace: dict[str, str]) -> str:
    value = entry.findtext(path, default="", namespaces=namespace)
    return value or ""


def _feed_datetime(entry: dict) -> datetime:
    published = entry.get("published") or entry.get("updated")
    if isinstance(published, str) and published:
        try:
            return parsedate_to_datetime(published).astimezone(timezone.utc)
        except (TypeError, ValueError):
            return datetime.now(timezone.utc)
    return datetime.now(timezone.utc)


def _iso_datetime(value: str) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _entry_authors(entry: dict) -> tuple[str, ...]:
    authors = entry.get("authors")
    if isinstance(authors, list):
        return tuple(_clean(author.get("name", "")) for author in authors if _clean(author.get("name", "")))
    author = _clean(entry.get("author", ""))
    return (author,) if author else ()


def _dedupe(items: tuple[CollectedItem, ...]) -> list[CollectedItem]:
    by_url = {item.url: item for item in items}
    return list(by_url.values())


def _clean(value: str) -> str:
    return " ".join(str(value).split())

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from tech_idea_digest.classifier import classify_item
from tech_idea_digest.collectors import collect_all
from tech_idea_digest.config import load_sources
from tech_idea_digest.emailer import send_digest_email
from tech_idea_digest.models import CollectedItem, Source
from tech_idea_digest.ranker import rank_items
from tech_idea_digest.render import render_digest


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        errors: list[tuple[str, str]] = []
        items = _sample_items() if args.sample_data else collect_all(load_sources(args.sources), on_error=errors.append)
        for source_id, message in errors:
            print(f"warning: skipped source {source_id}: {message}", file=sys.stderr)
        classified = [classify_item(item) for item in items]
        ranked = rank_items(classified, max_items=args.max_items)
        digest = render_digest(ranked)

        if args.send_email:
            send_digest_email(digest)
        if args.dry_run or not args.send_email:
            print(digest.body)
        return 0
    except Exception as exc:
        print(f"tech-idea-digest failed: {exc}", file=sys.stderr)
        return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send a ranked daily technology ideas digest.")
    parser.add_argument("--sources", default="sources.yaml", help="Path to curated sources YAML.")
    parser.add_argument("--max-items", type=int, default=20, help="Maximum ranked items in the digest.")
    parser.add_argument("--dry-run", action="store_true", help="Print the digest instead of only sending email.")
    parser.add_argument("--send-email", action="store_true", help="Send the digest using SMTP environment variables.")
    parser.add_argument("--sample-data", action="store_true", help="Use built-in sample data without network calls.")
    return parser


def _sample_items() -> list[CollectedItem]:
    source = Source(
        id="sample-arxiv",
        name="Sample arXiv",
        type="arxiv",
        tier=1,
        trust_score=0.95,
        categories=("AI/ML",),
        max_items=3,
        query="cat:cs.AI",
    )
    now = datetime.now(timezone.utc)
    return [
        CollectedItem(
            title="Agentic memory architectures for autonomous coding workflows",
            summary="A paper-style sample about long-term memory for autonomous software agents with benchmark results.",
            url="https://example.com/sample-agent-memory",
            published_at=now,
            source=source,
            authors=("Sample Researcher",),
        ),
        CollectedItem(
            title="Cloud security runtime isolation benchmark",
            summary="An engineering-style sample describing container isolation, security evaluation, and production results.",
            url="https://example.com/sample-cloud-security",
            published_at=now,
            source=source,
            authors=("Sample Platform Team",),
        ),
    ]


if __name__ == "__main__":
    raise SystemExit(main())

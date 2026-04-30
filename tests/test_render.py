from datetime import datetime, timezone

from tech_idea_digest.models import RankedItem, Source
from tech_idea_digest.render import render_digest


def test_render_digest_groups_items_by_category_and_shows_ranking_score():
    source = Source(
        id="arxiv-ai",
        name="arXiv AI",
        type="arxiv",
        tier=1,
        trust_score=1.0,
        categories=("AI/ML",),
        max_items=5,
        query="cat:cs.AI",
    )
    item = RankedItem(
        title="Agentic Memory Architectures",
        summary="A paper proposes long-term memory for autonomous software agents.",
        url="https://example.com/paper",
        published_at=datetime(2026, 4, 30, tzinfo=timezone.utc),
        source=source,
        authors=("A. Researcher",),
        category="Agents & Automation",
        matched_keywords=("agent", "memory"),
        score=91,
        signals=("source-quality", "recent", "relevance"),
    )

    digest = render_digest([item], generated_at=datetime(2026, 4, 30, tzinfo=timezone.utc))

    assert "Daily Technology Ideas Digest - 2026-04-30" in digest.subject
    assert "Score: 91/100" in digest.body
    assert "Category: Agents & Automation" in digest.body
    assert "Title: Agentic Memory Architectures" in digest.body
    assert "Why it matters:" in digest.body
    assert "Source: arXiv AI (Tier 1)" in digest.body

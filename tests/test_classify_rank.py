from datetime import datetime, timedelta, timezone

from tech_idea_digest.classifier import classify_item
from tech_idea_digest.models import CollectedItem, Source
from tech_idea_digest.ranker import rank_items


def make_source(source_id="arxiv-ai", tier=1, trust_score=1.0):
    return Source(
        id=source_id,
        name="arXiv AI",
        type="arxiv",
        tier=tier,
        trust_score=trust_score,
        categories=("AI/ML",),
        max_items=5,
        query="cat:cs.AI",
    )


def make_item(title, summary, source=None, published_at=None):
    return CollectedItem(
        title=title,
        summary=summary,
        url="https://example.com/item",
        published_at=published_at or datetime.now(timezone.utc),
        source=source or make_source(),
        authors=("A. Researcher",),
    )


def test_classify_item_assigns_specific_technology_category():
    item = make_item(
        "Agentic memory for large language model automation",
        "A retrieval augmented generation system improves autonomous coding agents.",
    )

    classified = classify_item(item)

    assert classified.category == "Agents & Automation"
    assert "agentic" in classified.matched_keywords


def test_classify_item_does_not_match_short_keywords_inside_words():
    systems_source = Source(
        id="arxiv-systems",
        name="arXiv Systems",
        type="arxiv",
        tier=1,
        trust_score=0.95,
        categories=("Cloud & DevOps",),
        max_items=5,
        query="cat:cs.SE",
    )
    item = make_item(
        "What Is the Cost of Energy Monitoring? An Empirical Study on RAPL-Based Tools",
        "The Running Average Power Limit interface estimates software energy consumption.",
        source=systems_source,
    )

    classified = classify_item(item)

    assert classified.category != "AI/ML"
    assert "rag" not in classified.matched_keywords


def test_rank_items_filters_low_quality_tier3_without_confirming_source():
    low_quality = make_item(
        "Random viral AI claim",
        "A social post claims a breakthrough without paper or engineering details.",
        source=make_source("community", tier=3, trust_score=0.7),
    )
    high_quality = make_item(
        "Scalable database replication protocol",
        "A paper describes distributed database consistency and replication benchmarks.",
        source=make_source("arxiv-systems", tier=1, trust_score=0.95),
    )

    ranked = rank_items([classify_item(low_quality), classify_item(high_quality)], max_items=10)

    assert [item.title for item in ranked] == ["Scalable database replication protocol"]
    assert ranked[0].score >= 70
    assert "source-quality" in ranked[0].signals


def test_rank_items_prioritizes_recent_relevant_items():
    recent = classify_item(
        make_item(
            "New cloud security runtime isolation benchmark",
            "Security isolation for cloud containers with benchmark results.",
            source=make_source("arxiv-security", tier=1, trust_score=0.96),
        )
    )
    old = classify_item(
        make_item(
            "Older frontend rendering pattern",
            "A web performance article about frontend rendering.",
            source=make_source("github-engineering", tier=2, trust_score=0.86),
            published_at=datetime.now(timezone.utc) - timedelta(days=10),
        )
    )

    ranked = rank_items([old, recent], max_items=2)

    assert ranked[0].title == "New cloud security runtime isolation benchmark"
    assert ranked[0].score > ranked[1].score


def test_rank_items_limits_results_per_category_for_balanced_digest():
    ai_items = [
        classify_item(
            make_item(
                f"Large language model benchmark {index}",
                "An AI paper with language model benchmark results.",
                source=make_source(f"arxiv-ai-{index}", tier=1, trust_score=1.0),
            )
        )
        for index in range(4)
    ]
    security = classify_item(
        make_item(
            "Cloud security isolation benchmark",
            "A security paper with isolation benchmark results.",
            source=make_source("arxiv-security", tier=1, trust_score=0.96),
        )
    )

    ranked = rank_items([*ai_items, security], max_items=5, max_per_category=2)

    categories = [item.category for item in ranked]
    assert categories.count("AI/ML") == 2
    assert "Security" in categories

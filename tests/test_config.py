import pytest

from tech_idea_digest.config import load_sources


def test_load_sources_keeps_only_enabled_allowlisted_sources(tmp_path):
    config = tmp_path / "sources.yaml"
    config.write_text(
        """
sources:
  - id: arxiv-ai
    name: arXiv AI
    type: arxiv
    tier: 1
    trust_score: 1.0
    enabled: true
    categories: ["AI/ML"]
    query: "cat:cs.AI"
    max_items: 5
  - id: disabled-feed
    name: Disabled Feed
    type: rss
    tier: 2
    trust_score: 0.8
    enabled: false
    categories: ["Cloud & DevOps"]
    url: "https://example.com/feed"
    max_items: 5
""",
        encoding="utf-8",
    )

    sources = load_sources(config)

    assert [source.id for source in sources] == ["arxiv-ai"]
    assert sources[0].tier == 1
    assert sources[0].trust_score == 1.0


def test_load_sources_rejects_untrusted_source(tmp_path):
    config = tmp_path / "sources.yaml"
    config.write_text(
        """
sources:
  - id: random-feed
    name: Random Feed
    type: rss
    tier: 3
    trust_score: 0.2
    enabled: true
    categories: ["AI/ML"]
    url: "https://example.com/feed"
    max_items: 5
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="trust_score"):
        load_sources(config)

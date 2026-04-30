from datetime import timezone

import tech_idea_digest.collectors as collectors
from tech_idea_digest.collectors import parse_arxiv_feed, parse_rss_feed
from tech_idea_digest.models import Source


def test_parse_rss_feed_normalizes_entries():
    source = Source(
        id="engineering",
        name="Engineering Blog",
        type="rss",
        tier=2,
        trust_score=0.85,
        categories=("Cloud & DevOps",),
        max_items=2,
        url="https://example.com/feed",
    )
    feed = """
<rss version="2.0">
  <channel>
    <title>Engineering Blog</title>
    <item>
      <title>Runtime isolation benchmark</title>
      <link>https://example.com/runtime</link>
      <description>Container security benchmark results.</description>
      <pubDate>Thu, 30 Apr 2026 00:00:00 GMT</pubDate>
      <author>platform@example.com</author>
    </item>
  </channel>
</rss>
"""

    items = parse_rss_feed(source, feed)

    assert len(items) == 1
    assert items[0].title == "Runtime isolation benchmark"
    assert items[0].source == source
    assert items[0].published_at.tzinfo == timezone.utc


def test_parse_arxiv_feed_extracts_authors_and_summary():
    source = Source(
        id="arxiv-ai",
        name="arXiv AI",
        type="arxiv",
        tier=1,
        trust_score=1.0,
        categories=("AI/ML",),
        max_items=2,
        query="cat:cs.AI",
    )
    feed = """
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Agentic memory architectures</title>
    <id>https://arxiv.org/abs/2604.12345</id>
    <summary>Long-term memory for autonomous coding agents.</summary>
    <published>2026-04-30T00:00:00Z</published>
    <author><name>A. Researcher</name></author>
  </entry>
</feed>
"""

    items = parse_arxiv_feed(source, feed)

    assert len(items) == 1
    assert items[0].url == "https://arxiv.org/abs/2604.12345"
    assert items[0].authors == ("A. Researcher",)
    assert "Long-term memory" in items[0].summary


def test_fetch_text_uses_certifi_tls_context(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return b"ok"

    def fake_urlopen(request, timeout, context):
        captured["timeout"] = timeout
        captured["context"] = context
        captured["user_agent"] = request.headers["User-agent"]
        return FakeResponse()

    monkeypatch.setattr(collectors.certifi, "where", lambda: "ca-bundle.pem")
    monkeypatch.setattr(collectors.ssl, "create_default_context", lambda cafile: f"context:{cafile}")
    monkeypatch.setattr(collectors, "urlopen", fake_urlopen)

    content = collectors._fetch_text("https://example.com/feed")

    assert content == "ok"
    assert captured["timeout"] == 30
    assert captured["context"] == "context:ca-bundle.pem"
    assert captured["user_agent"].startswith("tech-idea-digest/")


def test_collect_all_skips_failed_sources_and_reports_error(monkeypatch):
    ok_source = Source(
        id="ok",
        name="OK Feed",
        type="rss",
        tier=2,
        trust_score=0.8,
        categories=("Cloud & DevOps",),
        max_items=1,
        url="https://example.com/ok",
    )
    failing_source = Source(
        id="fail",
        name="Failing Feed",
        type="rss",
        tier=2,
        trust_score=0.8,
        categories=("Cloud & DevOps",),
        max_items=1,
        url="https://example.com/fail",
    )
    item = collectors.CollectedItem(
        title="Reliable source item",
        summary="A cloud benchmark result.",
        url="https://example.com/item",
        published_at=collectors.datetime.now(collectors.timezone.utc),
        source=ok_source,
    )

    def fake_collect_source(source):
        if source.id == "fail":
            raise RuntimeError("network failure")
        return [item]

    errors = []
    monkeypatch.setattr(collectors, "collect_source", fake_collect_source)

    items = collectors.collect_all([ok_source, failing_source], on_error=errors.append)

    assert items == [item]
    assert errors == [("fail", "network failure")]

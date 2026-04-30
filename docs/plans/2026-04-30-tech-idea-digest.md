# Tech Idea Digest Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a daily GitHub Actions-powered tool that finds high-quality technology ideas from selected academic and engineering sources, ranks them, and sends an English email digest.

**Architecture:** Implement a Python CLI with separate modules for source configuration, collection, classification, ranking, digest rendering, and SMTP delivery. Keep source quality explicit through an allowlisted `sources.yaml` file with tier, category hints, trust score, and per-source limits.

**Tech Stack:** Python 3.11+, `feedparser`, `PyYAML`, `pytest`, GitHub Actions, SMTP secrets.

---

### Task 1: Project Scaffold And Config

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `sources.yaml`
- Create: `README.md`

**Steps:**
1. Add package metadata and dependencies.
2. Add curated source configuration with Tier 1 academic sources and Tier 2 official engineering/research feeds.
3. Document required GitHub Actions secrets and local run commands.

### Task 2: Core Tests First

**Files:**
- Create: `tests/test_config.py`
- Create: `tests/test_classify_rank.py`
- Create: `tests/test_render.py`

**Steps:**
1. Write failing tests for loading and validating curated source config.
2. Write failing tests for technology category classification and ranking gates.
3. Write failing tests for English digest rendering with ranking scores.
4. Run `python -m pytest` and verify tests fail because implementation is missing.

### Task 3: Core Implementation

**Files:**
- Create: `tech_idea_digest/__init__.py`
- Create: `tech_idea_digest/models.py`
- Create: `tech_idea_digest/config.py`
- Create: `tech_idea_digest/classifier.py`
- Create: `tech_idea_digest/ranker.py`
- Create: `tech_idea_digest/render.py`

**Steps:**
1. Implement immutable dataclasses for sources and collected items.
2. Implement config loading and validation.
3. Implement keyword-based category classification.
4. Implement transparent 0-100 ranking with minimum quality gates.
5. Implement plain-text email digest rendering.
6. Run `python -m pytest` and verify tests pass.

### Task 4: Collectors, Email, And CLI

**Files:**
- Create: `tech_idea_digest/collectors.py`
- Create: `tech_idea_digest/emailer.py`
- Create: `tech_idea_digest/__main__.py`
- Create: `tests/test_collectors.py`
- Create: `tests/test_cli.py`

**Steps:**
1. Write tests for RSS/arXiv parsing and dry-run CLI behavior.
2. Implement RSS and arXiv collectors.
3. Implement SMTP email sender using environment variables.
4. Implement CLI options for dry run, source config path, max items, and send email.
5. Run `python -m pytest`.

### Task 5: GitHub Actions

**Files:**
- Create: `.github/workflows/daily-tech-digest.yml`

**Steps:**
1. Add daily cron workflow.
2. Install Python dependencies.
3. Run tests before sending.
4. Run digest CLI with SMTP secrets.

### Task 6: Final Verification

**Commands:**
- `python -m pytest`
- `python -m tech_idea_digest --dry-run --max-items 5`

**Expected Result:** Tests pass and dry-run prints a ranked digest without sending email.

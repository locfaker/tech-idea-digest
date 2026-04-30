# Tech Idea Digest

Daily ranked technology ideas digest from curated academic and engineering sources.

The tool collects from an allowlisted `sources.yaml`, classifies each item by technology area, applies source-quality gates, ranks the strongest signals, and sends an English plain-text email digest through GitHub Actions.

## Quick Use

GitHub Actions is the easiest way to use this project:

1. Push this repository to GitHub.
2. Add SMTP secrets in `Settings -> Secrets and variables -> Actions`.
3. Open `Actions -> Daily Technology Ideas Digest`.
4. Click `Run workflow`.
5. First run with `send_email` off to preview the digest.
6. Run again with `send_email` on when the preview looks right.

See [docs/setup-github-actions.md](docs/setup-github-actions.md) for the step-by-step setup.

## What It Prioritizes

- Tier 1 academic sources such as arXiv category searches.
- Tier 2 official research and engineering feeds from established technology organizations.
- Explicit trust scores and per-source limits in `sources.yaml`.
- Ranking transparency: each item includes score, category, source tier, and signals.

Tier 3/community sources are intentionally excluded from the first implementation unless you later add cross-source confirmation logic.

## Local Setup

Use a real Python executable. On this machine, the working interpreter is:

```powershell
& 'C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe' -m pip install -e .[dev]
```

Run tests:

```powershell
& 'C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe' -m pytest
```

Run an offline sample digest:

```powershell
& 'C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe' -m tech_idea_digest --dry-run --sample-data --max-items 5
```

Run against live sources without sending email:

```powershell
& 'C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe' -m tech_idea_digest --dry-run --max-items 10
```

## Email Secrets

Configure these GitHub repository secrets before enabling the scheduled workflow:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `EMAIL_TO`

Optional:

- `SMTP_USE_TLS`: defaults to `true`; set to `false` only for a trusted SMTP endpoint that does not support STARTTLS.

For Gmail, use an App Password instead of the main account password.

## Source Curation

Edit `sources.yaml` to add or disable feeds. Keep source quality strict:

- Use Tier 1 for structured academic sources.
- Use Tier 2 for official research, engineering, cloud, and security feeds.
- Keep `trust_score` at `0.5` or higher for enabled sources.
- Prefer source-specific `max_items` limits to avoid noisy daily emails.

## GitHub Actions

The workflow in `.github/workflows/daily-tech-digest.yml` runs daily, installs dependencies, runs tests, and sends the digest via SMTP.

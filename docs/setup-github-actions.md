# Setup GitHub Actions For Tech Idea Digest

This guide is the short version for using the tool from GitHub.

## 1. What The Tool Does

Every run does this:

1. Reads curated sources from `sources.yaml`.
2. Collects papers and engineering posts.
3. Filters weak sources.
4. Classifies items by technology group.
5. Ranks the best ideas.
6. Shows a digest preview in GitHub Actions.
7. Sends email only when scheduled or when `send_email` is enabled manually.

## 2. Add GitHub Secrets

Open the repository:

```text
https://github.com/VoDaiLocz/tech-idea-digest
```

Then go to:

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

Add these secrets:

```text
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
EMAIL_FROM
EMAIL_TO
```

For Gmail, use:

```text
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-gmail-address@gmail.com
SMTP_PASSWORD=your-gmail-app-password
EMAIL_FROM=your-gmail-address@gmail.com
EMAIL_TO=where-you-want-to-receive-the-digest
```

Do not use your normal Gmail password. Use a Gmail App Password.

## 3. Run Manually

Go to:

```text
Actions -> Daily Technology Ideas Digest -> Run workflow
```

Leave `send_email` off for the first test. The workflow will:

- install Python dependencies
- run tests
- generate a digest preview
- upload `digest.txt` as an artifact
- show the digest in the workflow summary

After the preview looks right, run it again with `send_email` enabled.

## 4. Daily Schedule

The workflow runs every day at:

```text
00:00 UTC
```

That is:

```text
07:00 Asia/Bangkok
```

Scheduled runs send email automatically.

## 5. Change Sources

Edit `sources.yaml`.

Use:

- `enabled: true` to include a source
- `enabled: false` to pause a source
- `max_items` to reduce noise
- `trust_score` to control quality

Keep low-quality/community sources out of Tier 1 and Tier 2.

# 0005. Structured feedback flow

- **Status:** Accepted (user decision, 2026-11-17)
- **Date:** 2026-11-16

## Context

Non-technical reviewers must be able to comment in a structured way, each comment tied to a requirement or clause ID, separately from author pull requests. The demo has only GitHub available. See [feedback notes](../research/feedback-l10n-publishing.md).

## Options

1. GitHub Issue Forms with per-requirement prefilled links
2. giscus threads mapped to requirement IDs
3. Hypothesis annotation
4. Self-hosted comment servers or a hosted web form relay

## Decision

Use **GitHub Issue Forms**: an ISO-style comment form (requirement ID, comment type, comment, proposed change, organisation), opened from a link beside each requirement with the ID prefilled. A workflow validates the ID against the built requirement list. `make feedback-export` produces a disposition matrix. Reviewers without a GitHub account use a spreadsheet template with the same columns, which a maintainer checks and imports with `make feedback-import` (one issue per row).

## Consequences

- Comments are triageable, labelled, exportable and permanently linked to an ID.
- Commenting directly requires a GitHub account; the spreadsheet path is slower and maintainer-mediated.
- A hosted web form for account-less commenting is the production answer but needs a third-party service; it is documented, not built.

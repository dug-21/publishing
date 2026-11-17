# Feedback, translation, publishing and CI

Checked 2026-11-16. *Unverified* means not confirmed from a current source that day.

## Structured feedback from non-technical reviewers

| Candidate | Health | Fit |
|---|---|---|
| GitHub Issue Forms | Platform feature | **Pick.** Required fields and dropdowns; fields prefill from URL query parameters by field `id`. Needs a GitHub account. |
| giscus | No tagged releases; last commit 2026-05-26 | Runner-up. Can map a thread to a specific term such as a requirement ID. Good for discussion, weak for triage. Needs a GitHub account. |
| Hypothesis | Client released 2026-11-12 | Anchors to text ranges, not clause IDs; needs its own account. |
| Remark42 1.18.0, Isso 0.14.0 | Active | Need a server; out of scope for a GitHub-only demo. |
| utterances, Staticman, Commento++ | Dormant since 2020–2022 | Reject. |

How standards bodies do it (*from memory, unverified today*): ISO/IEC use a comment-template table (clause, comment type, comment, proposed change, secretariat observation); NIST uses comment-matrix spreadsheets and, for some projects, GitHub issues; W3C uses GitHub issues; PCI SSC uses a portal restricted to participating organisations.

**Recommended flow:**

1. An Issue Form with ISO-style fields: requirement ID, comment type, comment, proposed change, organisation.
2. A "Comment on this requirement" link beside every requirement in the HTML, prefilled with its ID.
3. A workflow on `issues: opened` that checks the ID against the built requirement list and labels or replies if it is invalid.
4. `make feedback-export`, producing a CSV/XLSX disposition matrix from the labelled issues.
5. For people without a GitHub account: a downloadable spreadsheet template with the same columns, imported by a maintainer through a manually triggered workflow that creates one issue per row.

Caveats: prefill is documented for text fields, so the requirement ID is an `input`, not a dropdown. URL `labels=` only applies for users with triage rights, so labels are set in the template. A hosted web form is the production answer for account-less commenting, but it needs a third-party service or a token-holding relay, so it is documented rather than built.

## Translation

| Tool | Version / date | Notes |
|---|---|---|
| sphinx-intl | 2.4.0 (2026-08-30) | **Pick.** Standard for Sphinx: gettext builder → PO files → per-locale builds. |
| po4a | 0.74 (2025-07-12) | Pick if the source were AsciiDoc. |
| Weblate | 2026.11.2 (2026-11-12), GPL-3.0 | Git-native; reads PO and XLIFF. Optional platform. Free hosting for libre projects *unverified*. |
| Crowdin, Transifex | SaaS | Not checked today. |
| mkdocs-static-i18n, Docusaurus | — | Directory-per-locale; weaker change tracking. |

PO is the interchange format because translators never touch markup and fuzzy flags show which translations went stale when a normative clause changed. XLIFF, if a vendor needs it, comes from Weblate export or translate-toolkit.

RTL: set `lang` and `dir="rtl"` per edition and use CSS logical properties. The HTML → WeasyPrint PDF path rendered Arabic in the [spike](spike-pdfua.md).

Demo scope (agreed 2026-11-17): a partially translated Spanish edition plus a Japanese smoke test. No right-to-left language is included, so RTL is not proven by the demo.

## Publishing and CI

| Item | Version / date |
|---|---|
| actions/checkout | v7.0.1 (2026-07-20) |
| actions/configure-pages | v6.0.0 (2026-03-25) |
| actions/upload-pages-artifact | v5.0.0 (2026-04-10) |
| actions/deploy-pages | v5.0.1 (2026-09-01) |
| actions/attest | v4.2.2 (2026-08-04) |
| git-cliff | 2.14.2 (2026-09-18) |
| softprops/action-gh-release | v3.0.4 (2026-11-05) |
| mike | 2.2.0 (2026-04-14), MkDocs-only |
| sphinx-multiversion | 0.2.4, effectively unmaintained |
| devcontainers/ci | v0.3.1900000450 (2026-06-01) |

- **Site:** the three official Pages actions. Versioned as plain `/vX.Y/` directories plus `/latest/` and a `versions.json` switcher. The Pages artifact replaces the whole site, so the built site is kept on a `gh-pages` branch and that branch is uploaded.
- **Releases:** tag `v*` → `make publish` → `gh release create` with git-cliff notes. `gh` runs identically locally. release-please and semantic-release target package releases and are more than an editorially versioned standard needs.
- **Provenance:** `actions/attest` on the PDF, OSCAL JSON, XLSX and site tarball; verified with `gh attestation verify`.
- **Pinning:** actions by full commit SHA with a version comment; Dependabot for `github-actions` and `devcontainers`.
- **Local/CI parity:** one pinned tool image, used by the devcontainer and as the CI job container, calling the same `make` targets. devcontainers/ci is the runner-up: truer parity but slower, and Docker-in-Docker features add friction. Installing tools on the runner is rejected because it drifts.

## Sources

<https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema>, <https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue>, <https://giscus.app/>, <https://po4a.org/>, <https://docs.weblate.org/en/latest/formats.html>, <https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds>, release pages of each repository named.

# 0007. Publishing, releases and CI

- **Status:** Accepted (user decision, 2026-11-17)
- **Date:** 2026-11-16

## Context

Validation runs on pull requests, publishing on merge and tag, with one entry point used identically locally and in CI, and every version pinned. See [publishing notes](../research/feedback-l10n-publishing.md).

## Decision

- **Entry point:** `make check`, `make build`, `make publish`, with one target per validation layer underneath.
- **Environment:** one toolbox image defined in `tools/Dockerfile`, with every tool pinned. The Makefile runs every target inside it, locally and in CI. The image tag is a hash of the files that define it, so a change to any pin rebuilds it. The devcontainer only needs Docker and Make.
- **Site:** GitHub Pages through `actions/configure-pages`, `upload-pages-artifact` and `deploy-pages`; versions as `/vX.Y/` directories plus `/latest/`.
- **Releases:** a `v*` tag runs `make publish` and `gh release create` with the PDF, OSCAL JSON, CSV/XLSX and site archive; notes from git-cliff 2.14.2; provenance from `actions/attest`.
- **Pinning:** actions by commit SHA, tools by exact version, containers by digest; Dependabot proposes updates.

## Options not chosen

- devcontainers/ci: truest parity but slower.
- mike and sphinx-multiversion: MkDocs-only and unmaintained respectively.
- release-please and semantic-release: built for package releases.

## Consequences

- CI cannot drift from local runs, because both call the same targets in the same image.
- The first run builds the toolbox image (several minutes, about 3 GB); CI caches its layers.
- Provenance attestation runs only when the repository is public. Private repositories are believed to need GitHub Enterprise Cloud for attestations (not verified).
- Keeping old versions on the site means the built site lives on a `gh-pages` branch that the deploy job uploads.

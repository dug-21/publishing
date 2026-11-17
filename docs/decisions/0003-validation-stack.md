# 0003. Validation stack

- **Status:** Accepted (user decision, 2026-11-17)
- **Date:** 2026-11-17

## Context

Validation must be layered, each layer runnable on its own, failing the build with actionable messages. The source is AsciiDoc (ADR 0001), which has no requirement model, so requirement rules are ours to implement. See [validators notes](../research/validators.md).

## Decision

| Layer | Tool |
|---|---|
| Syntax, includes, internal cross-references | Asciidoctor with `--failure-level WARN` |
| Required sections, requirement IDs, required fields, procedure linkage | JSON Schema over `requirements.json` with check-jsonschema 0.39.0 |
| Uniqueness, numbering, normative-keyword placement | one small rule script over `requirements.json` and the document structure |
| Terminology and prose style | Vale 3.27.0 with project rules |
| Spelling | cspell 10.5.1 |
| External links and anchors | lychee 0.24.2 over built HTML |
| HTML validity | Nu Html Checker (`vnu-jar` 26.11.14) |
| HTML accessibility | axe-core 4.14 via Playwright, WCAG 2.0–2.2 A/AA tags |
| PDF accessibility | veraPDF 1.30.4, PDF/UA-1 |
| OSCAL | see ADR 0004 |

Each layer gets its own `make` target and its own failure fixture.

## Consequences

- Custom code is the extractor plus one rule script; everything else is an established tool.
- Vale does not follow AsciiDoc includes and scopes by markup element, so it lints each clause file directly and normative files are identified by path.
- Java is required (Nu Html Checker, veraPDF, oscal-cli); veraPDF and oscal-cli run from pinned containers.
- The pipeline reports "automated accessibility checks pass", not WCAG or PDF/UA conformance; reading order and alt-text quality need human review.

# Phase 1 research: toolchain evaluation

**Date checked:** 2026-11-16. Versions and dates were read that day from GitHub releases, PyPI, RubyGems, npm, Docker Hub, the VS Code Marketplace and official docs. Anything not confirmed that day is marked *unverified* in the notes.

Criteria are those in [`KeyRequirements.md`](../../KeyRequirements.md). Decisions are recorded as ADRs in [`docs/decisions/`](../decisions/).

> **Updated 2026-11-17.** `KeyRequirements.md` gained a **Scale** criterion (about 400 pages) and a sharper **Low author friction**. All three leading candidates were then built at 400 pages; see [bakeoff-400-pages.md](bakeoff-400-pages.md). The matrix below includes those results. Plain Asciidoctor was re-scored because the HTML → WeasyPrint path removes its tagged-PDF objection.

> **Decision (2026-11-17): AsciiDoc with plain Asciidoctor.** The matrix below scores Sphinx higher; the user chose AsciiDoc for its tables and cross-referencing in a long document, accepting the extra custom code for requirement tooling. See [ADR 0001](../decisions/0001-source-format-and-build.md). The picks further down reflect that decision.

## Notes per category

| File | Covers |
|---|---|
| [source-formats.md](source-formats.md) | Authoring format and build toolchain, PDF path, VS Code ecosystem |
| [validators.md](validators.md) | Prose, syntax, links, HTML, accessibility, PDF/UA, structural rules |
| [oscal-grc.md](oscal-grc.md) | OSCAL model and tooling, GRC import formats, spreadsheet libraries |
| [feedback-l10n-publishing.md](feedback-l10n-publishing.md) | Structured commenting, translation, Pages, releases, CI |
| [bakeoff-400-pages.md](bakeoff-400-pages.md) | Three-way build at 400 pages: Sphinx, plain Asciidoctor, Metanorma |
| [spike-pdfua.md](spike-pdfua.md) | Hands-on check that the proposed PDF path produces PDF/UA |

## Scored matrix: source format and build toolchain

This is the decision everything else hangs from. Scores are 0–3 (0 = cannot meet the criterion, 3 = meets it out of the box). They are judgements from the notes, not measurements. A 0 on any criterion disqualifies the candidate regardless of total.

| Criterion | Sphinx + MyST + sphinx-needs | Metanorma | Quarto (Pandoc + Typst) | Asciidoctor (+ Antora) | DITA-OT | MkDocs Material | Bikeshed / ReSpec |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Plain-text, diffable source | 3 | 3 | 3 | 3 | 2 | 3 | 2 |
| Structured, standards-grade output | 2 | 3 | 1 | 1 | 3 | 1 | 2 |
| Machine-checkable | 3 | 3 | 1 | 2 | 3 | 1 | 1 |
| Multi-format (HTML, PDF, OSCAL source data) | 2 | 3 | 3 | 2 | 2 | 1 | **0** |
| Feedback (stable per-requirement anchors to hang comments on) | 3 | 2 | 2 | 2 | 2 | 2 | 3 |
| Reproducible (pinned, light install) | 3 | 2 | 3 | 3 | 2 | 3 | 3 |
| Open source, maintained, ecosystem (incl. VS Code) | 3 | 2 | 3 | 2 | 1 | 1 | 2 |
| Low author friction | 2 | 2 | 3 | 2 | **0** | 3 | 1 |
| Accessibility (HTML and tagged PDF) | 2 | 1 | 3 | 3 | 2 | 2 | 3 |
| Translation | 3 | 1 | 1 | 2 | 3 | 2 | 1 |
| Consumption (extractable requirement data) | 3 | 2 | 1 | 1 | 3 | 1 | 1 |
| Scale (400 pages, measured) | 2 | 1 | not tested | 3 | not tested | not tested | not tested |
| **Total** | **31 of 36** | **25 of 36** | 24 of 33 | **26 of 36** | 23 of 33 (disqualified) | 20 of 33 | 19 of 33 (disqualified) |

Changes from the bake-off: Asciidoctor's multi-format and accessibility scores rose (its PDF passed PDF/UA through WeasyPrint); Metanorma's accessibility score fell (its PDF failed PDF/UA with default settings). Low author friction was not re-scored; the bake-off did not measure it.

Why the leading candidates score as they do:

- **Sphinx + MyST + sphinx-needs** is the only candidate with requirement objects that export to JSON *and* a built-in gettext translation flow *and* a pure-Python pinned install. It loses points on standards structure (clause numbering and normative/informative conventions are ours to define) and on PDF (the accessible path is assembled from HTML + WeasyPrint, not built in). The spike shows that path works.
- **Metanorma** has the best native standards model. It loses on translation (no PO workflow, RTL fixes last seen in 2021), single-vendor release churn, a heavy Ruby + Java stack, and no dedicated editor tooling.
- **Plain Asciidoctor** was the cleanest at scale and handles complex tables better than Markdown, but it has no requirement model: ID checks and data extraction for OSCAL and spreadsheets would all be custom code, and translation would use po4a.
- **Quarto** has the most turnkey validated PDF/UA and friendly authoring, but no requirement model, so structure, checks and extraction would all be custom filters.

## Picks for the other categories

These had clearer answers and are summarised here; reasoning is in the notes and ADRs.

| Layer | Pick | Runner-up |
|---|---|---|
| PDF generation | WeasyPrint 70.0 from Asciidoctor HTML, `pdf/ua-1` variant | Typst 0.15 via Pandoc |
| Prose, style, terminology | Vale 3.27.0 | textlint 16.1.0 |
| Spelling | cspell 10.5.1 | codespell 2.4.3 |
| Source syntax and cross-references | Asciidoctor `--failure-level WARN` | — |
| Structure and requirement rules | extractor → `requirements.json`; JSON Schema (check-jsonschema 0.39.0) + one small rule script | conftest |
| External links | lychee 0.24.2 over built HTML | linkinator 8.1.0 |
| HTML validity | Nu Html Checker (`vnu-jar` 26.11.14) | html-validate 11.21.1 |
| HTML accessibility | axe-core 4.14 via Playwright, WCAG 2.0–2.2 A/AA tags | IBM Equal Access 4.0.35 |
| PDF accessibility | veraPDF 1.30.4, PDF/UA-1 profile | — |
| OSCAL generation | small emitter from `requirements.json` | compliance-trestle 5.2.1 |
| OSCAL validation | check-jsonschema against pinned NIST schema, then oscal-cli 3.2.0 (metaschema-framework) | go-oscal 0.7.2 |
| Spreadsheet export | XlsxWriter 3.3.1 (+ CSV from the stdlib) | — |
| Feedback | GitHub Issue Forms, prefilled per requirement, plus a spreadsheet template for people without accounts | giscus |
| Translation | po4a 0.74, PO files (Weblate-compatible) | directory per locale |
| Site | GitHub Pages via `actions/deploy-pages`, `/vX.Y/` directories | mike |
| Releases | tag → `make publish` → `gh release create`, notes from git-cliff 2.14.2, `actions/attest` provenance | softprops/action-gh-release |
| CI parity | one pinned tool image used by the devcontainer and by CI jobs | devcontainers/ci |

## Custom code this leaves us writing

Choosing AsciiDoc means four pieces of custom code, all small and all built around one file:

1. **Requirement extractor** — walks the parsed document through the Asciidoctor API and writes `requirements.json`.
2. **Rule script** — uniqueness, sequential numbering, procedure linkage, and "normative keywords only in normative clauses".
3. **OSCAL emitter** — `requirements.json` → OSCAL catalog JSON.
4. **Spreadsheet export** — `requirements.json` → CSV/XLSX.

Everything downstream reads `requirements.json`, so the source is parsed once, by Asciidoctor itself.

## Limits to state plainly

- **Automated accessibility checks do not prove conformance.** axe-core has one WCAG 2.2-specific rule, off by default. veraPDF machine-checks only part of PDF/UA. The pipeline can claim "automated checks pass"; reading order and alt-text quality need a human.
- **oscal-cli 3.2.0 bundles OSCAL 1.2.1 bindings**, while the latest OSCAL is 1.2.3. The 1.2.2 and 1.2.3 releases made no model changes, so the catalog will declare `oscal-version` 1.2.1 unless 1.2.3 is accepted in testing.
- **Items to confirm in Phase 2:** the Asciidoctor HTML and stylesheet pass axe; po4a segments the requirement convention and complex tables sensibly; WeasyPrint keeps passing veraPDF with images, footnotes and merged-cell tables.

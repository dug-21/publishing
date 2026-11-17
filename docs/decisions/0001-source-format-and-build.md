# 0001. Source format and build toolchain

- **Status:** Accepted (user decision, 2026-11-17)
- **Date:** 2026-11-17

## Context

The standard needs a plain-text source in Git that technical and non-technical subject-matter experts can write, at a scale of about 400 pages and several hundred requirements. Requirements (stable ID, text, testing procedures, guidance) must be validated and extracted for OSCAL and spreadsheet exports. See [the scored matrix](../research/README.md), [source-formats notes](../research/source-formats.md) and the [400-page bake-off](../research/bakeoff-400-pages.md).

## Options

1. Sphinx + MyST Markdown + sphinx-needs (31/36)
2. Plain Asciidoctor with HTML → WeasyPrint PDF (26/36)
3. Metanorma (25/36)
4. Quarto with Pandoc and Typst (24/33, not scale-tested)
5. DITA-OT, MkDocs Material, Bikeshed/ReSpec (disqualified or not recommended)

## Decision

Use **AsciiDoc built with plain Asciidoctor**. Source is one file per clause or annex, assembled with includes. Requirements, testing procedures and guidance follow a fixed AsciiDoc convention (anchored IDs and roles). A small extractor built on the Asciidoctor API writes `requirements.json`, the single extraction point for structural checks, the OSCAL catalog and the spreadsheet export.

The matrix scored Sphinx higher. The user chose AsciiDoc for its stronger tables and cross-referencing in a long document, accepting more custom code, on the grounds that requirement tooling has to be built for GRC consumption in any case.

## Consequences

- Complex tables (block content in cells, merged cells) and cross-references are first-class in the source.
- It was the cleanest candidate at 400 pages: built and passed PDF/UA with no tuning.
- There is no built-in requirement model. We own the requirement convention, the extractor, and the ID, numbering and linkage checks (ADR 0003).
- Translation uses po4a rather than a built-in flow (ADR 0006).
- Asciidoctor core releases slowly (2.0.26, 2025-10-24), though the project is active.
- Editor support is one well-maintained VS Code extension (~766k installs) with live preview; snippets for the requirement block reduce friction.
- Form-style authoring for non-technical authors is a possible later enhancement over the same source, not part of this build.
- Sphinx + sphinx-needs is the fallback if the custom requirement tooling proves too costly.

# Bake-off at 400 pages

**Date:** 2026-11-17. **Why:** `KeyRequirements.md` now names a 400-page standard as a valid test case, and the first scale test of the recommended toolchain failed (see [spike-pdfua.md](spike-pdfua.md)).

## Test document

A synthetic standard with the same content in each format: 12 clauses, 336 requirements, 1,008 testing procedures, guidance prose and about 1,000 internal cross-references (roughly 1 MB of source). No images, footnotes or merged-cell tables. All tools ran in disposable containers or a scratch virtual environment; nothing was installed in the devcontainer.

## Results

| | Sphinx + MyST + sphinx-needs | Plain Asciidoctor | Metanorma (CalConnect flavor) |
|---|---|---|---|
| Versions | Sphinx 9.2.0, MyST-Parser 5.2.0, sphinx-needs 9.2.0, WeasyPrint 70.0 | `asciidoctor/docker-asciidoctor` (latest tag), WeasyPrint 70.0 | `metanorma/metanorma` (latest tag) |
| Source → HTML | 5–8 s | under 20 s including container start | part of the 163 s below |
| PDF step | 67 s, about 1.1 GB | 42 s, about 570 MB | 163 s for XML + HTML + PDF together |
| Pages | 399 | 345 | 286 |
| veraPDF PDF/UA-1 | compliant, 0 failures | compliant, 0 failures | **not compliant**: 3 rules failed 1,099 times each, all on link annotations (clauses 7.18.1 and 7.18.5) |
| Requirement data out | `needs.json`, 1,344 objects, no extra code | none; needs custom extraction | Metanorma XML, 336 `<requirement>` elements |
| Configuration needed to get here | custom requirement layout and plain theme (3 lines) | none | none, but two of three flavors tried were blocked |

Page counts differ because of default styling density, not missing content.

## Findings per candidate

### Sphinx + MyST + sphinx-needs

- With default settings the PDF step took 588 s and failed PDF/UA 1,344 times (an untagged icon on every requirement). A plain requirement layout fixed both.
- Internal links between requirements and testing procedures are malformed in the single-page HTML (`#document-clause-01#TP_1_1_A`), so they would not work in the PDF without a fix.
- sphinx-needs renders each requirement as an HTML layout table. It passed PDF/UA, but layout tables are an accessibility concern for the HTML and may need a custom template.

### Plain Asciidoctor

- Passed first time with no tuning, built with warnings treated as failures.
- It has no requirement model. This run checked nothing about requirement IDs and extracted no requirement data; that would be custom code (an Asciidoctor extension, or parsing the DocBook or HTML output).

### Metanorma

- The ISO and OGC flavors both stopped at Fontist's font licence prompt (`--agree-to-terms`), which was not accepted. The CalConnect flavor built without it.
- The PDF/UA failures match the open upstream issue on link annotation tagging (mn2pdf #293). The build also logged about 1,100 unresolved link destinations, so the untuned test source may contribute.
- The OGC flavor reported every requirement that had no linked conformance test before it stopped. That built-in linkage check is something the other two candidates need configuration or code for.

## What this does not show

- Authoring experience. The benchmark measures build behaviour, not how the source feels to a non-technical author or how complex tables are edited.
- Behaviour with images, footnotes, merged-cell or multi-page tables, or translated editions.
- That Metanorma cannot pass PDF/UA; only that it did not with default settings on this source.
- Container image tags were not pinned for Asciidoctor and Metanorma, so those versions are "latest on 2026-11-17".

# Source formats and build toolchains

Checked 2026-11-16. Open-issue counts include pull requests. *Unverified* means not confirmed from a current source that day.

## Sphinx + MyST Markdown + sphinx-needs — recommended

- **Versions:** Sphinx 9.2.0 (2026-10-21, BSD-2-Clause); MyST-Parser 5.2.0 (2026-11-10, MIT); sphinx-needs 9.2.0 (2026-11-04, MIT, backed by useblocks).
- **Structure:** custom need types (requirement, testing procedure, guidance) with stable IDs, typed links between them, per-type ID regex, and schema validation with severities. The `needs` builder writes `needs.json`, which is the extraction point for OSCAL and spreadsheets. Clause numbering and normative/informative marking are conventions we define.
- **PDF:** the LaTeX builder does not tag (Sphinx issue #13134 is open). Use HTML → WeasyPrint 70.0 instead; see [spike-pdfua.md](spike-pdfua.md).
- **HTML accessibility:** depends on theme. Furo and PyData are reasonable starting points (*unverified*; gate with axe).
- **Translation:** strongest of the candidates. Built-in gettext builder plus sphinx-intl 2.4.0 (2026-08-30). PO files are the format Weblate and Crowdin expect.
- **Author friction:** MyST is Markdown with directives. Requirement blocks need directive syntax, which a template and snippets can cover.
- **VS Code:** generic Markdown tooling is very large (Markdown All in One ~15.0M installs, markdownlint ~12.6M). MyST-specific support is thin (`myst-highlight` ~63k, last updated 2021). `useblocks.ubcode` (~6k) gives sphinx-needs lint and preview. reStructuredText extension ~791k.
- **Install:** pure Python, pinned through uv. WeasyPrint needs Pango system libraries.
- **Risks:** accessible PDF is an assembled path; sphinx-needs is used mostly in automotive/safety engineering rather than by standards bodies (*unverified*).
- Sources: <https://github.com/sphinx-doc/sphinx/issues/13134>, <https://sphinx-needs.readthedocs.io/en/latest/builders.html>, <https://doc.courtbouillon.org/weasyprint/stable/changelog.html>

## Metanorma — runner-up

- **Versions:** metanorma-cli 1.18.6 (2026-11-12, BSD-2-Clause), released every 2–4 days; mn2pdf 2.74 (2026-11-11).
- **Users:** the PDF Association co-maintains a flavor with Ribose. ISO, IEC, OGC, ITU and BIPM use is *unverified* today.
- **Structure:** best fit. ModSpec blocks (`[requirement]`, `[recommendation]`, `[permission]`, `[conformance_test]`) carry a mandatory unique identifier, a guidance part, and tests linked to requirements. They are emitted in Metanorma XML.
- **PDF:** mn2pdf (Apache FOP) is actively worked toward PDF/UA-1, but conformance is not guaranteed; mn2pdf #425 and #293 are open.
- **Translation:** language and script attributes and localized boilerplate, but no gettext/PO workflow; RTL fixes last seen in 2021.
- **VS Code:** no Metanorma extension found; authors use the generic AsciiDoc extension (~766k installs).
- **Install:** Docker image bundling Ruby and Java. Pinned image tags *unverified*.
- **Risks:** effectively single-vendor, very fast release churn, heavy stack, flavor templates assume a standards body's house style.
- Sources: <https://rubygems.org/gems/metanorma-cli>, <https://www.metanorma.org/author/topics/blocks/requirements-modspec/>, <https://github.com/metanorma/mn2pdf/issues/425>

## Quarto (Pandoc + Typst)

- **Versions:** Quarto 1.11.9 (2026-10-30); Pandoc 3.14 (2026-11-12, GPL-2.0); Typst 0.15.1 (2026-07-17, Apache-2.0).
- **PDF:** the most turnkey. Since Quarto 1.9 a `pdf-standard` option gives PDF/UA-1 via Typst or UA-2 via LaTeX with built-in veraPDF validation. Typst tags by default since 0.14 and fails the build on PDF/UA violations.
- **Structure:** no requirement object; divs plus Lua filters would be custom work for structure, checks and extraction.
- **Translation:** weak, no PO workflow (*unverified*).
- **VS Code:** `quarto.quarto` ~536k installs with preview; `tinymist` (Typst) ~253k.
- **Note:** Typst's own HTML export is still behind a feature flag, so Typst alone cannot be the single source.
- Sources: <https://opensource.posit.co/blog/2026-03-05_pdf-accessibility-and-standards/>, <https://typst.app/docs/changelog/0.15.0/>

## Asciidoctor (+ asciidoctor-pdf, Antora)

- **Versions:** Asciidoctor 2.0.26 (2025-10-24, MIT), no core release in about 13 months; asciidoctor-pdf 2.3.27 (2026-09-12); Antora 3.2.0 (2026-08-28).
- **PDF:** asciidoctor-pdf does not produce tagged PDF (issue #2582 closed without a fix; Prawn lacks tagging). This alone rules out its native PDF path.
- **Structure:** no requirement object; roles and attributes plus a custom extension.
- **Translation:** po4a 0.74 treats AsciiDoc as a first-class format.
- **VS Code:** `asciidoctor.asciidoctor-vscode` 4.3.0 (2026-11-05), ~766k installs, live preview and diagnostics.
- Source: <https://github.com/asciidoctor/asciidoctor-pdf/issues/2582>

## DITA + DITA-OT — disqualified on author friction

- DITA-OT 4.4.2 (2026-11-14, Apache-2.0). Strong XML semantics and XLIFF translation, but raw XML is not workable for subject-matter experts without a paid editor, and VS Code support is tiny (~1.4k installs).

## MkDocs Material — not recommended

- MkDocs core is still 1.6.1 (2024-08-30). Material entered maintenance mode in November 2025 (9.8.1 shipped 2026-11-07); its successor Zensical is at 0.1.1. No native PDF and no requirement model.
- Source: <https://squidfunk.github.io/mkdocs-material/blog/2025/11/11/insiders-now-free-for-everyone/>

## Bikeshed / ReSpec — disqualified on PDF

- Bikeshed 7.2.1 (2026-11-02, CC0); ReSpec 37.6.0 (2026-11-15). Both are HTML-only with no PDF pipeline, HTML-heavy source, and W3C conventions built in. VS Code support is tiny (~2.5k installs).

## VS Code ecosystem at a glance

| Format | Main extension | Installs | Maintained |
|---|---|---|---|
| Markdown (generic) | Markdown All in One / markdownlint | ~15.0M / ~12.6M | yes |
| reStructuredText | lextudio.restructuredtext | ~791k | yes |
| AsciiDoc | asciidoctor.asciidoctor-vscode | ~766k | yes |
| Quarto | quarto.quarto | ~536k | yes |
| Typst | tinymist | ~253k | yes |
| MyST | myst-highlight | ~63k | stale (2021) |
| sphinx-needs | useblocks.ubcode | ~6k | yes |
| Bikeshed, DITA | various | <3k | — |
| Metanorma | none found | — | — |

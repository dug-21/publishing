# 0002. PDF generation

- **Status:** Accepted (user decision, 2026-11-17)
- **Date:** 2026-11-17

## Context

The PDF must be tagged and accessible. Asciidoctor's own PDF converter (asciidoctor-pdf) does not tag. See [source-formats notes](../research/source-formats.md) and the [PDF/UA spike](../research/spike-pdfua.md).

## Options

1. WeasyPrint 70.0 over the Asciidoctor HTML, `pdf/ua-1` variant
2. Typst 0.15 via Pandoc (enforced PDF/UA-1)
3. asciidoctor-pdf (untagged)
4. DocBook → Apache FOP

## Decision

Generate the PDF with **WeasyPrint 70.0 from the Asciidoctor HTML output** with a print stylesheet, and gate it with veraPDF's PDF/UA-1 profile.

## Consequences

- HTML and PDF share one rendering of the content, so structure and requirement markup cannot drift between formats.
- At 400 pages this path took 42 s and passed veraPDF PDF/UA-1 with 0 failures ([bake-off](../research/bakeoff-400-pages.md)); images, footnotes and merged-cell tables are still to be proven.
- WeasyPrint needs Pango system libraries in the tool image.
- Print features such as running headers and page-numbered cross-references rely on CSS paged media.
- Typst is the fallback if WeasyPrint fails veraPDF on real content.

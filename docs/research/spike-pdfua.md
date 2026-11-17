# Spike: does HTML → WeasyPrint produce valid PDF/UA?

**Date:** 2026-11-16. **Why:** the recommended toolchain has no built-in tagged-PDF path, and the desk research could not confirm that WeasyPrint output passes a PDF/UA validator.

## What was run

- **Input:** a small HTML document with headings, an internal link, a table with a caption and row/column header scopes, a list, and a right-to-left Arabic paragraph.
- **Generator:** WeasyPrint 70.0 in a throwaway `python:3.13-slim-bookworm` container, `weasyprint --pdf-variant pdf/ua-1 in.html out.pdf`.
- **Validator:** `verapdf/cli:v1.30.4 --flavour ua1`.

## Result

veraPDF reported the file compliant with the PDF/UA-1 profile: 106 rules passed, 0 failed (1,281 checks).

## Scale check: a 400-page document

A synthetic standard was generated to test the path at PCI DSS scale: 12 clauses, 336 requirements, each with prose, a three-row testing-procedure table with a caption and header scopes, guidance and internal links (1.1 MB of HTML).

| Measure | Result |
|---|---|
| Pages | 437 |
| WeasyPrint time | 36 s |
| WeasyPrint peak memory | about 460 MB |
| PDF size | 1.9 MB |
| veraPDF PDF/UA-1 | compliant; 106 rules passed, 0 failed (2,971,757 checks) in 17 s |

The synthetic content has no images, footnotes, wide or multi-page tables, or generated page-number cross-references, and it did not go through Sphinx, so Sphinx and sphinx-needs build time at this scale is not measured here.

## Scale check through the real toolchain (2026-11-17)

The same synthetic standard was then written as MyST Markdown with sphinx-needs objects (336 requirements and 1,008 testing procedures, 1,344 objects in 12 clause files) and built with Sphinx 9.2.0, MyST-Parser 5.2.0 and sphinx-needs 9.2.0, default settings and the default theme.

| Step | Result |
|---|---|
| Sphinx HTML build | 8 s |
| Sphinx single-page HTML build | 6 s (3.5 MB) |
| `needs.json` | 1,344 objects exported |
| WeasyPrint → PDF | **588 s, about 1.7 GB peak memory**, 434 pages |
| veraPDF PDF/UA-1 | **not compliant**: 1 rule failed 1,344 times (clause 7.3, figure without alternative text), one per sphinx-needs object |

Reading of this result:

- Sphinx and sphinx-needs themselves are fast at this scale.
- The default sphinx-needs HTML rendering is not usable for the PDF as it stands. Each object carries an image with no alternative text, and its markup makes WeasyPrint about 16 times slower than the hand-written HTML in the first scale check.
- Both problems are in the rendering, not the source. The expected fix is a custom sphinx-needs layout and a lean print stylesheet. That fix is **not yet proven**.

### Metanorma comparison attempt

An equivalent AsciiDoc document was compiled with the `metanorma/metanorma` container using the ISO flavor. It parsed the 1 MB source and then stopped after 66 s: the flavor's fonts are downloaded by Fontist, which requires accepting font licence terms (`--agree-to-terms`). That acceptance was not given, so Metanorma's build time and PDF/UA result at this scale are **not measured**.

## What this does and does not show

- It shows the path is viable and that the veraPDF `ua1` flavour flag works in the pinned container.
- It does not show that the full sample standard will pass; long tables, footnotes, a table of contents and the bibliography are untested. That is what the Phase 2 output check is for.
- It does not show the PDF reads well in a screen reader. veraPDF checks structure, not reading order or alt-text quality.
- Nothing was installed into the devcontainer; both tools ran in disposable containers.

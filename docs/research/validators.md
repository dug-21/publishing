# Validation tooling

Checked 2026-11-16. *Unverified* means not confirmed from a current source that day.

## Prose, style and terminology

- **Pick: Vale 3.27.0** (2026-11-12; three releases in four weeks; MIT, *licence unverified*).
  - Markdown is built in. YAML rule types (`existence`, `substitution`, `occurrence`, `consistency`, `conditional`) cover normative keywords and defined-term checks.
  - Scopes are by markup element, not named section. "Normative keywords only in normative clauses" therefore relies on one file per clause or annex and per-glob rules in `.vale.ini`.
  - Style packages for Microsoft, Google, write-good, proselint and alex exist (*unverified today*), which makes those standalone tools redundant.
- **Runner-up: textlint 16.1.0** (2026-11-16, MIT). Active, Markdown-first.
- **Spelling: cspell 10.5.1** (2026-11-14, MIT). Alternative: codespell 2.4.3 (2026-07-15, GPL-2.0-only), lower noise.
- **Avoid:** write-good 1.0.8 (2021) and alex 11.0.1 (2023) are stale; proselint 0.16.0 (2025-11-14) is slow-moving.

## Source syntax and cross-references

- **Pick: `sphinx-build -W --keep-going`** with nitpicky mode on Sphinx 9.2.0. Broken internal references and malformed directives become build failures with file and line.
- markdownlint-cli2 0.24.1 (2026-11-12, MIT) is available if plain-Markdown style rules are wanted; MyST directives need rule exclusions.

## Structure and requirement rules

- **Pick: sphinx-needs 9.2.0 built-in checks** — per-type ID regex, required fields and link validation with severities, `needs_warnings`; duplicate-ID errors (*unverified*).
- **Plus JSON Schema over `needs.json`** with check-jsonschema 0.39.0 (2026-10-26) for required sections and field shapes.
- **Plus one small script** for what neither can express: sequential numbering and keyword placement across items.
- **Not chosen:** conftest 0.71.1 (Rego is another language for contributors); Schematron (natural only with an XML source).

## External links

- **Pick: lychee 0.24.2** (2026-05-01, Apache-2.0 or MIT). Single binary, fragment checking, cache, official GitHub Action. Run over built HTML so rendered anchors are checked too. No release for about six months; worth watching.
- **Runner-up:** Sphinx `linkcheck`; linkinator 8.1.0 (2026-08-29).
- **Avoid:** htmltest 0.17.0 (2022) is stale.

## HTML validity

- **Pick: Nu Html Checker**, the W3C reference checker; npm `vnu-jar` 26.11.14 (2026-11-14, MIT). Needs Java.
- **Runner-up: html-validate 11.21.1** (2026-11-12, MIT). Node-only and offline, but not the reference parser.

## HTML accessibility

- **Pick: axe-core 4.14.1** (2026-11-16, MPL-2.0) via `@axe-core/playwright` 4.14.0.
  - Request tags explicitly: `wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa`. Only one rule (`target-size`) carries the 2.2 tag, and it is off by default.
- **Runner-up: IBM Equal Access `accessibility-checker` 4.0.35** (2026-11-13, Apache-2.0) as a second engine.
- **Not chosen:** pa11y 10.0.0 / pa11y-ci 5.0.0 (no WCAG 2.2 standard offered); Lighthouse CI 0.16.1 (a subset of axe, score-oriented).
- **Limit:** no automated tool proves WCAG 2.2 AA conformance.

## PDF accessibility

- **Pick: veraPDF 1.30.4** (Docker `verapdf/cli:v1.30.4`, 2026-11-09, GPL-3.0). The `--flavour ua1` profile was exercised in the [spike](spike-pdfua.md).
- **Supplement:** qpdf 12.4.2 `--check` for structural integrity only.
- **Limit:** machine checks cover part of PDF/UA; PAC is Windows-only freeware, suitable for manual spot checks, not CI.

## VS Code extensions

| Extension | Installs | Last updated |
|---|---|---|
| Code Spell Checker (cspell) | 18.6M | 2026-10-15 |
| markdownlint | 12.6M | 2026-08-02 |
| axe Accessibility Linter | 654k | 2026-10-26 |
| Vale VSCode (ChrisChinchilla) | 93k | 2026-11-10 |
| html-validate | 76k | 2026-11-12 |

The old `errata-ai.vale-server` extension is dead (2022); do not use it.

## Sources

<https://github.com/errata-ai/vale/releases>, <https://github.com/dequelabs/axe-core> (`doc/rule-descriptions.md`), <https://github.com/lycheeverse/lychee>, <https://software.verapdf.org/releases>, <https://hub.docker.com/r/verapdf/cli>, <https://sphinx-needs.readthedocs.io>, npm and PyPI registries, VS Code Marketplace.

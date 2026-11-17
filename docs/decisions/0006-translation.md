# 0006. Translation workflow

- **Status:** Accepted (user decision, 2026-11-17)
- **Date:** 2026-11-17

## Context

The source and toolchain must support translated editions, including right-to-left scripts. The source is AsciiDoc (ADR 0001). See [translation notes](../research/feedback-l10n-publishing.md).

## Options

1. po4a with PO files
2. Directory-per-locale copies of the source (optionally through Weblate's AsciiDoc format)
3. Antora components per locale

## Decision

Use **po4a 0.74**, which treats AsciiDoc as a first-class format. English is the source; `l10n/po/<lang>.po` holds translations; po4a generates a translated source tree per locale, which builds through the same pipeline with `lang` and `dir` set. A keep-threshold fails the build for editions below an agreed translated percentage. The demo ships a partially translated Spanish edition and a Japanese smoke test (CJK fonts and line breaking). At the user's request the demo does not include a right-to-left language, so RTL output is supported by design but not proven here. PO files are compatible with Weblate, documented as the optional translator-facing platform.

## Consequences

- Translators never edit markup, and fuzzy flags show which translations went stale when a clause changed.
- Requirement IDs stay identical across editions, so OSCAL and feedback links are language-independent.
- po4a releases slowly (last release 2025-07-12); it is a Perl tool and a system dependency.
- How well po4a segments the requirement convention and complex tables must be confirmed early in Phase 2.
- Stylesheets must use CSS logical properties for RTL.

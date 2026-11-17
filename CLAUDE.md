# CLAUDE.md

## Purpose

This repository builds a **complete, working demonstration of a technical-standards pipeline**: authoring → automated validation → publishing. It is a demo, but every part must actually run — no mock stages, no "TODO: wire up CI".

The work has two phases, done in order:

1. **Research** — evaluate tooling and frameworks against the core criteria below and record a decision.
2. **Build** — implement the chosen toolchain end to end, with a sample standard that exercises every validation and publishing step.

## Core criteria

All tool and framework choices are judged against the requirements in @KeyRequirements.md. Change that file first if a criterion changes.

## Phase 1: Research

- Compare realistic candidates across categories, e.g. source formats (AsciiDoc, Markdown variants, Metanorma, reStructuredText/Sphinx, Bikeshed/ReSpec, DITA), validators (prose and style linters, schema checks, link checkers, custom rule engines), OSCAL tooling (e.g. compliance-trestle, oscal-cli), structured feedback/commenting for non-technical reviewers, accessibility and translation/localization support, and publishing/CI (GitHub Actions, Pages, release tooling).  Include in the decision criteria dev/authoring ecosystems that support VS Code like plugins.  No need to elicit every plugin, just size/scale of options.
- Use current sources (official docs, release history, issue activity); note the date and version checked. Don't rely on memory for maintenance status.
- Record results in `docs/research/` — a scored matrix against the criteria plus short notes per candidate.
- Record each choice as an ADR in `docs/decisions/NNNN-title.md` (context, options, decision, consequences).
- Design a proposed high-level workflow from the research and add a summary-level Mermaid diagram of it to `README.md`.
- Present the recommendation to the user and get agreement **before** starting Phase 2.

## Phase 2: Build

Deliverables:

- **Sample standard** — a realistic, small but complete standard modeled on the *structure* of PCI DSS: scope, normative references, terms, several normative clauses, tables, an informative annex, bibliography. Each requirement has a stable ID, the requirement text, testing procedures, and guidance. Content must be original — do not copy PCI DSS text (it is copyrighted). It should exercise every feature the pipeline claims to support.
- **Validation**, layered and each runnable on its own:
  - source/syntax and structure (required sections, numbering, IDs)
  - requirement language (normative keywords only in normative clauses, every requirement uniquely identified)
  - cross-references and external links resolve
  - terminology consistency (defined terms used as defined)
  - prose/style lint
  - output checks (build succeeds, HTML is valid, PDF generated, OSCAL validates against the NIST schemas)
  - accessibility (WCAG-conformant HTML, tagged PDF)
- **Deliberate failure fixtures** — sample inputs that should fail each validator, so the checks are proven, not assumed.
- **Publishing** — from one source: HTML, PDF, OSCAL catalog, and a GRC-friendly spreadsheet export (CSV/XLSX of requirements, testing procedures, guidance); versioned releases (tag → release artifacts); published site (e.g. GitHub Pages). Structure the source so translated editions are possible.
- **Feedback** — a working structured-comment flow for non-technical reviewers, with each comment tied to a requirement or clause ID. This is separate from author changes, which go through pull requests.
- **CI** — GitHub Actions running validation on PRs and publishing on merge/tag.
- **One entry point** — a single command (e.g. `make check`, `make build`, `make publish`) used identically locally and in CI.

## Environment

Devcontainer (`.devcontainer/`) on Ubuntu Noble with Node LTS, Python, Rust, Docker-in-Docker, `gh`, `jq`, and `yq`. Add new system dependencies to `.devcontainer/postCreate.sh` or a container image — not ad hoc installs — so the pipeline stays reproducible. Pin every tool version.

## Working rules

- Keep it as simple as the criteria allow; prefer an established tool over custom code, and write custom validators only for gaps the research identified.
- Update `README.md` as things land: what the pipeline does and how to run each step.
- Verify by running it: a stage counts as done when its command passes on valid input and fails on its failure fixture.
- Commit and push only when the user asks.

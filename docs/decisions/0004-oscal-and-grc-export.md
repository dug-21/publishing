# 0004. OSCAL catalog and GRC export

- **Status:** Accepted (user decision, 2026-11-17)
- **Date:** 2026-11-17

## Context

One source must also yield an OSCAL catalog that validates against the NIST schemas, and a spreadsheet GRC tools can import. See [OSCAL and GRC notes](../research/oscal-grc.md).

## Options

1. Small emitter from `requirements.json`
2. compliance-trestle 5.2.1 catalog authoring
3. Hand-maintained OSCAL alongside the prose

## Decision

- **Generate** the catalog with a small Python emitter from `requirements.json`: clause → `group`; requirement → `control`; text → `statement`; testing procedures → `assessment-method` with one ID-bearing `item` per procedure; guidance → `guidance`.
- **Validate** with check-jsonschema against the pinned NIST catalog schema, then **oscal-cli 3.2.0** (metaschema-framework) for constraints beyond the schema.
- **Export** CSV and XLSX (XlsxWriter 3.3.1): one row per requirement, plus a second sheet with one row per testing procedure.

## Consequences

- The emitter is custom code; trestle's catalog authoring is shaped around NIST 800-53 and would not remove it.
- oscal-cli bundles OSCAL 1.2.1 bindings; the catalog declares 1.2.1 unless 1.2.3 is accepted in testing (no model changes between them).
- Stable testing-procedure IDs let OSCAL assessment plans and results reference the standard later.
- There is no standard GRC column layout; ours is flat and avoids characters some importers reject. Tool-specific layouts can be added as further exports.

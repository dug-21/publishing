# OSCAL and GRC consumption

Checked 2026-11-16. *Unverified* means not confirmed from a current source that day.

## OSCAL itself

- **Latest:** v1.2.3 (2026-08-07), a patch release with no model changes; 1.2.2 (2026-04-30) likewise.
- **Governance:** NIST still hosts and releases it. The OSCAL Foundation co-leads model development in partnership with NIST. No evidence found of a formal handover (*unverified either way*).
- **Schemas:** published as release assets (`oscal_catalog_schema.json`, `.xsd`); pin by release tag.
- **Published examples:** PCI SSC publishes no OSCAL. CIS has `CISecurity/CISControls_OSCAL` (marked work in progress). FedRAMP publishes baselines. NIST's own tutorial models an ISO 27002 excerpt.

## Proposed catalog mapping

| Standard element | OSCAL |
|---|---|
| Clause / section | `group` |
| Requirement | `control` with `id`, `title`, `props` (`label`, `sort-id`) |
| Requirement text | `part` named `statement` |
| Testing procedures | `part` named `assessment-method`, one child `item` part per procedure, each with a stable ID |
| Guidance | `part` named `guidance` |

Stable IDs on the testing procedures are what let an OSCAL assessment plan or results file point back at them.

## Tooling

| Tool | Version / date | OSCAL | Notes |
|---|---|---|---|
| metaschema-framework/oscal-cli | 3.2.0, 2026-05-15 | 1.2.1 bindings | The live fork. Java 17 or container. The only tool that checks Metaschema constraints beyond the schema. |
| usnistgov/oscal-cli | 1.0.3, 2024-02-02 | — | No release in over two years; stale. |
| compliance-trestle | 5.2.1, 2026-11-10 | 1.2.0–1.2.1 | CNCF sandbox, monthly releases, Apache-2.0. Catalog authoring is 800-53-shaped and there is no CSV-to-catalog task (*from memory; docs site was unreachable*). |
| go-oscal | 0.7.2, 2026-10-20 | tracks 1.2.3 | Single binary, schema-level validation only. |
| check-jsonschema | 0.39.0, 2026-10-26 | any | Fast schema check, no JVM. |
| Lula, oscal-pydantic, npm `oscal` | — | — | Dropped OSCAL, dead, and stale respectively. Avoid. |

**Pick:** a small emitter from `needs.json`, validated by check-jsonschema against the pinned NIST schema and then by oscal-cli 3.2.0 for constraints. Declare `oscal-version` 1.2.1 unless oscal-cli accepts 1.2.3 in testing.

## GRC import formats

CSV/XLSX is the universal format. OSCAL-native import is limited to federal-leaning tools.

| Tool | Import |
|---|---|
| ServiceNow | OSCAL catalog/profile/SSP in the CAM workspace |
| RegScale | OSCAL-native, plus Excel/JSON |
| Hyperproof | CSV template, case-sensitive headers, up to 4 section levels |
| Drata | CSV of requirements; `<`, `>` and `\` disallowed |
| Vanta | "Import sections" spreadsheet |
| eramba | Compliance-package CSV |
| CISO Assistant | XLSX loaded directly or converted to YAML |
| Archer, OneTrust | Not found; assume CSV/Excel |

There is no standard column layout. **Recommended export:**

- Sheet 1, one row per requirement: `requirement_id, section, section_title, title, requirement_text, testing_procedures, guidance, version`.
- Sheet 2, one row per testing procedure: `procedure_id, requirement_id, text`.
- No embedded HTML and none of `<`, `>`, `\`.

## Testing against the standard

OSCAL assessment-plan / assessment-results is the natural pairing, since they reference catalog control and part IDs directly. XCCDF and InSpec suit automated technical checks rather than procedural testing; OCSF is an event schema.

## Spreadsheet libraries

- **XlsxWriter 3.3.1** (2026-10-28, BSD-2-Clause) — pick; write-only and actively maintained.
- openpyxl 3.1.5 (2024-06-28) — only for reading the file back in tests.
- SheetJS on npm is frozen at 0.18.5 (2022); avoid.

## Sources

<https://github.com/usnistgov/OSCAL/releases>, <https://pages.nist.gov/OSCAL/learn/tutorials/control/basic-catalog/>, <https://github.com/metaschema-framework/oscal-cli/releases>, <https://github.com/oscal-compass/compliance-trestle/releases>, <https://github.com/defenseunicorns/go-oscal/releases>, <https://github.com/CISecurity/CISControls_OSCAL/>, <https://docs.hyperproof.io/programs/creating-own-program>, <https://help.drata.com/en/articles/6346623-custom-framework>, <https://github.com/intuitem/ciso-assistant-community>.

# Publishing Requirements
Every tool or framework choice is judged against these. If a criterion is unclear or the user adds one, update this list first.

- **Plain-text, diffable source** — the standard lives in Git and author changes are reviewed as pull requests. (Public/stakeholder comments use the separate Feedback flow below.)
- **Structured, standards-grade output** — numbered clauses, normative vs. informative content, requirement... think PCI style requirements.  Assume public on the same global scale.
- **Machine-checkable** — validation can be automated and fails the build with actionable messages.
- **Multi-format publishing** — PDF, HTML, also OSCAL from a single source; versioned releases.
- **Feedback** - Tooling needs to support broad commenting (from nontechnical people) in a structured way
- **Reproducible** — pinned versions; the same command works locally, in the devcontainer, and in CI.
- **Open source and actively maintained** — prefer tools with a real user base in standards bodies or large doc projects.  Minimize (but doesn't have to eliminate) building custom tools.  Prefer toolsets with larger ecosystems for flexibility and to potentially reduce our development.
- **Low author friction** — authors are a mix of technical and non-technical subject-matter experts. A non-technical author can add or edit a requirement without learning the toolchain: little markup to memorise, a template or guided editing for requirement blocks, live preview, and clear error messages when something is wrong.
- **Scale** — a standard of around 400 pages and several hundred requirements is a valid test case. At that size the source stays navigable for authors (split by clause, complex tables remain editable), and build, validation and publishing still complete in a practical time.
- **Accessibility** — published HTML meets WCAG 2.2 AA and PDFs are tagged/accessible, as expected for a public standard at global scale.
- **Translation** — source and toolchain support producing translated editions (localization workflow, Unicode/RTL-capable output).
- **Consumption** - the output needs to support Imports to corporate GRC tools, as well as consumed for testing against the standards. 
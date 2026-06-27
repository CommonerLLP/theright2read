# Data & Code Availability — canonical template (R2R working-paper series)

Single source of truth for the Data & Code Availability (D&C) section across all
RTR working papers. Decided 2026-06-27 (see auto-memory `project-r2r-deposit-publication-plan`).

Each paper's D&C section has two parts:

1. **Per-paper clause** — names this paper's *derived artifacts* and its *primary
   sources* (varies per paper; keep concrete, never fabricate a file list).
2. **Invariant block** — identical across the series; do not reword per paper.

## Invariant block (paste verbatim; the two sentences below)

> The derived data and analysis code for this paper are deposited in the Right to
> Read working-paper series' Open Science Framework (OSF) project, with the code
> archived for a citable, versioned DOI on Zenodo (DOIs to be assigned at public
> release). Primary sources are cited to their own repositories rather than
> re-hosted here; the deposited derived data are released under CC-BY-4.0 and the
> analysis code under the GNU Affero General Public License v3 (AGPL-3.0).

## Routing (why those venues)

- Paper preprint → **SocArXiv** (OSF's social-science/humanities preprint server) → preprint DOI.
- Data + supplement → **OSF** project; one shared project for the whole series, each paper a component.
- Code → **GitHub (CommonerLLP)** → **Zenodo** release → software DOI.
- Copyrighted primary sources → **cite, do not re-host** (deposit only derived artifacts).
- Licensing: derived data **CC-BY-4.0**; code **AGPL-3.0**.

## Placement

D&C is `{.unnumbered}`, placed immediately before `# References`. If a paper has a
`# Funding and Competing Interests` / `# Acknowledgements` section, D&C follows it.
WP-008 is the reference implementation.

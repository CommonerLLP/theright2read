# The Right to Read

**Free public libraries for all.** A campaign for the reading commons India was promised and never given, and a reckoning with why.

→ **[theright2read.org](https://theright2read.org)**

The Right to Read is an anti-caste campaign for **free, tax-funded, universal public libraries** in India. This repository holds the campaign's website and its open research. The site makes one argument, in numbers and in history: the public library was built by India's emancipatory movements and refused by its State, and winning it back is a question of political will, not of money.

## The demand

Every person in India should have a free public library within reach: staffed, stocked, open, and funded by law rather than by a minister's mood. Not a subscription reading room, not a screen, not a scheme that can be zeroed by a revised estimate. A commons.

The claim is older than the Republic. In 1848 Jotirao Phule named reading itself as an anti-caste act and opened schools for the children caste had kept illiterate. The line runs through Periyar, through Travancore's P.N. Panicker and the Kerala library movement, to Tamil Nadu's statutory, cess-funded library system, to the demand this campaign makes now. Reading was withheld by caste for centuries. The free public library is where it is taken back.

## The finding

India spends about **₹4.77 per person per year** on public libraries, states and the Centre combined, in real terms. That is not a budget. It is a measure of how little a reading public is held to be owed. In real terms the figure has fallen 42 per cent from its 2018-19 peak. And where libraries survive, a documentary gate (a guarantor, a gazetted officer's signature, a refundable ₹3,000 deposit, a biometric) screens out the very readers they were built for.

Every number on the site cites a primary source. The full method and the evidence are in the working papers.

## On the site

| Page | What it is |
|---|---|
| **[/](https://theright2read.org/)** | The pamphlet: the demand |
| **[/status-quo/](https://theright2read.org/status-quo/)** | The money: what India spends, state by state |
| **[/history/](https://theright2read.org/history/)** | The history: how reading was refused |
| **[/act/](https://theright2read.org/act/)** | Write to your representative |
| **[/writing/](https://theright2read.org/writing/)** | The working papers and briefs |
| **[/library/](https://theright2read.org/library/)** | The reading room: the sources |

## The research

The campaign runs on a working-paper series. Each paper is public, cited, and reproducible:

- **RTR-WP-001**, *A Consolidated Real Per-Capita Series for Public Library Expenditure in India.* The ₹4.77 measurement.
- **RTR-WP-002**, *The Convergence Blueprint.* A tax-funded national public-library network by 2035.
- **RTR-WP-003**, *The Grammar of Refusal.* How the Centre's library funding was unmade by procedure, not by any decision on record.
- **RTR-WP-006**, *Whom Does the City Allow to Read?* Disclosure, reach, and the documentary gate in Ahmedabad and Delhi.
- **RTR-WP-008**, *From Reader to User.*

Read them at [theright2read.org/writing](https://theright2read.org/writing/).

## How to help

The campaign needs people more than it needs pull requests. In rough order of usefulness:

1. **Read it, share it, cite it.** The evidence only counts if it travels. Send the site to a librarian, a journalist, a councillor.
2. **Correct a fact.** If a number, date, or law is wrong, open an issue with a **primary source**: an official PDF, an annexure, a table, a gazette. Sourced corrections are the single most valuable contribution to this repository.
3. **Add to the record.** State Library Acts, budget lines, RRRLF releases, membership rules. If you hold a document the campaign is missing, bring it.
4. **Organise.** The demand is local. A library is won ward by ward.

Conduct here is governed by an anti-caste **[Code of Conduct](CODE_OF_CONDUCT.md)**: caste, including descent and work-and-descent-based discrimination, is a protected characteristic, and casteism has no place in this project.

## The code

The site is built to last with almost no maintenance: **static, no backend, no framework, no build step.** Any browser that runs ES2020 will serve it in 2035. Under the hood it is a small hexagonal core (`assets/core/`: a pure domain, thin ports, and swap-in render adapters), a single light-and-dark design-token system (`assets/tokens.css`), and generated content (the working-paper catalogue and the Zotero reading room are compiled from source, not hand-written). GitHub Pages serves it from `main`.

You are welcome to read, fork, and reuse the code, but rebuilding the site is not the point of this repository. To run it locally, contribute code, or refresh the parliamentary-record corpus, see **[CONTRIBUTING.md](CONTRIBUTING.md)**.

## Acknowledgements

With thanks to Open Budgets India (CivicDataLab) for opening up Indian budget data, on which much of this work rests.

## Licence

Code and content are released under the **[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0)** licence: noncommercial use only. For the underlying facts, cite the primary sources named on the site, not this repository. See [`LICENSE`](LICENSE).

# Ahmedabad and Toronto Public Libraries — research bundle

A self-contained copy of the Right 2 Read Campaign's comparative study of the
**Ahmedabad Public Library / M.J. Library Network** and the **Toronto Public
Library**: the paper, the figures, the underlying data, and the code that builds
the figures.

## The argument

Read against Ahmedabad's own decade of disclosures, the finding is not just that
Toronto is better resourced — it is that Ahmedabad's public library **use is
falling**:

- Annual circulation fell ~55% from its 2017-18 peak (212,397 → 96,491).
- New annual (active) members fell ~84% (3,194 → 505).
- The reported 26,834-member total is flat only because ~95% is a non-expiring
  lifetime roll; the active share is under 2%.
- The 2025-26 budget spends 61.7% on establishment/payroll and 1.4% on reading
  material.
- Per resident, Toronto outspends Ahmedabad on the order of 200× (nominal) but
  lends ~735× more — so funding levels alone do not explain the decline.
- A Metro or Janmarg/AJL BRTS corridor runs through every one of the worst-served
  peripheral wards, yet only 60 of 83 libraries are within 500 m of rapid transit:
  a library-**siting** gap, not a transit gap.

## Layout

```
paper/      ahmedabad-toronto-public-library-comparison.qmd  (Quarto source)
            library-comparator-references.bib                (bibliography)
            ahmedabad-toronto-public-library-comparison.html/.pdf  (rendered)
            figures/fig1..fig5 *.png                          (generated)
scripts/    make_library_paper_figures.py                     (figure generator)
            access_engine/                                    (upstream builders, reference)
data/       cities/ahmedabad/source/libraries/...             (M.J. Network disclosures)
            cities/ahmedabad/derived/library_access/...        (ward access proxy outputs)
            cities/ahmedabad/layers/*.geojson                  (wards, Metro, BRTS, AMTS, stops)
            cities/toronto/source|derived/libraries/...        (TPL open data + key facts)
            comparators/ahmedabad_toronto/...                  (IFLA metric comparison)
```

## Reproduce the figures

Needs `pandas`, `geopandas`, `matplotlib`. From this directory:

```
python3 scripts/make_library_paper_figures.py
```

It reads only the `data/` in this bundle and writes the five PNGs into
`paper/figures/`. Re-render the paper with Quarto:

```
quarto render paper/ahmedabad-toronto-public-library-comparison.qmd --to pdf
quarto render paper/ahmedabad-toronto-public-library-comparison.qmd --to html
```

## Provenance and data trust

Originated in the `sevent4` municipalities-atlas repository; this is a copied,
self-contained bundle for the Right 2 Read Campaign. Library figures come from the
M.J. Library Network's annual proactive (RTI) disclosures and budget tables, and
from Toronto Open Data / TPL published facts. Transit geometry (Metro, Janmarg/AJL
BRTS, AMTS) is AMC/GMRC/GTFS-sourced.

The ward walk-access numbers are a **ward-centroid proxy**, not scheduled-transit
routing; the access model's transit-time proxy is unfit (it beats walking in 0 of
48 wards) and is therefore **not** reported — the transit map uses routing-free
network geometry instead. The `scripts/access_engine/` files are the upstream
builders that produced `data/cities/ahmedabad/derived/library_access/`; their
import paths assume the original `sevent4` `scripts/recipes/` layout, so they are
included as method reference, while the derived outputs they produced are already
in `data/`.

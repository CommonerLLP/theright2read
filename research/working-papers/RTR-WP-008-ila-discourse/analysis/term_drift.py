#!/usr/bin/env python3
"""ILA proceedings term-drift, 1942-2019 (all 40 OCR'd volumes).

Reproducible recompute that supersedes the earlier partial 1942-2008 run.
Reads the OCR sidecar text for every volume, counts a fixed vocabulary
(case-insensitive, word-boundary; multi-word terms matched as phrases),
normalises per 10,000 words, and aggregates into six period bins.

Outputs (under data/ila-conference-proceedings/analysis/):
  term_counts_by_volume_1942_2019.csv
  term_drift_by_period_1942_2019.csv
  term_drift_summary_1942_2019.md

Run: python research/working-papers/RTR-WP-008-ila-discourse/analysis/term_drift.py
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ILA = ROOT / "data" / "ila-conference-proceedings"
TEXT = ILA / "ocr" / "text"
MANIFEST = ILA / "ocr_manifest.jsonl"
OUT = ILA / "analysis"

# term_name -> phrase to match (underscore => space). Word-boundary, optional
# trailing plural 's' on the final token. Case-insensitive.
TERMS = {
    "reader": "reader", "user": "user", "citizen": "citizen",
    "public_library": "public library", "rural": "rural",
    "adult_education": "adult education", "social_education": "social education",
    "literacy": "literacy", "legislation": "legislation", "finance": "finance",
    "information": "information", "documentation": "documentation",
    "network": "network", "computerization": "computer",  # computer/computeris/zation
    "quality": "quality", "management": "management", "technology": "technology",
    "digital": "digital", "knowledge": "knowledge",
    "lifelong_learning": "lifelong learning",
    "information_literacy": "information literacy",
    "caste": "caste", "language": "language", "labour": "labour",
}
PERIODS = [(1942, 1949), (1950, 1969), (1970, 1985),
           (1986, 1999), (2000, 2008), (2009, 2019)]


def period_of(year):
    for lo, hi in PERIODS:
        if lo <= year <= hi:
            return f"{lo}-{hi}"
    return "other"


def compile_pat(phrase):
    toks = phrase.split()
    toks[-1] = toks[-1] + r"s?"          # optional plural on last token
    body = r"\s+".join(toks)
    return re.compile(r"\b" + body + r"\b", re.IGNORECASE)


PATS = {k: compile_pat(v) for k, v in TERMS.items()}

# year/title from manifest, keyed by the text filename stem
meta = {}
for line in MANIFEST.read_text().splitlines():
    if not line.strip():
        continue
    r = json.loads(line)
    stem = Path(r["ocr_text_path"]).stem
    meta[stem] = (r.get("date_issued"), r.get("handle"), r.get("title", ""))

rows = []
for txt in sorted(TEXT.glob("*.txt")):
    stem = txt.stem
    year_s, handle, title = meta.get(stem, (stem[:4], "", ""))
    try:
        year = int(str(year_s)[:4])
    except (TypeError, ValueError):
        year = int(stem[:4])
    text = txt.read_text(errors="replace")
    words = len(re.findall(r"\w+", text))
    counts = {k: len(p.findall(text)) for k, p in PATS.items()}
    rows.append({"year": year, "handle": handle, "title": title,
                 "period": period_of(year), "words": words, **counts})

rows.sort(key=lambda r: (r["year"], r["title"]))

OUT.mkdir(parents=True, exist_ok=True)
cols = ["year", "handle", "title", "period", "words"] + list(TERMS)
with (OUT / "term_counts_by_volume_1942_2019.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow(r)

# aggregate by period
agg = {}
for r in rows:
    p = r["period"]
    a = agg.setdefault(p, {"volumes": 0, "words": 0,
                           **{k: 0 for k in TERMS}})
    a["volumes"] += 1
    a["words"] += r["words"]
    for k in TERMS:
        a[k] += r[k]

period_order = [f"{lo}-{hi}" for lo, hi in PERIODS]
with (OUT / "term_drift_by_period_1942_2019.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["period", "volumes", "words", "term", "count", "per_10k_words"])
    for p in period_order:
        a = agg.get(p)
        if not a:
            continue
        for k in TERMS:
            per10k = round(a[k] / a["words"] * 10000, 3) if a["words"] else 0
            w.writerow([p, a["volumes"], a["words"], k, a[k], per10k])

# markdown summary table (per-10k, key terms)
key_terms = ["reader", "user", "citizen", "public_library", "adult_education",
             "social_education", "information", "network", "computerization",
             "quality", "management", "digital", "knowledge", "technology",
             "caste", "language", "finance", "labour"]
lines = ["# ILA term drift, 1942-2019 (per 10,000 words)", "",
         "Fresh recompute over all 40 OCR'd volumes; supersedes the 1942-2008 run.",
         "Discovery counts, not final claims; page-level verification governs quotation.",
         ""]
hdr = "| term | " + " | ".join(period_order) + " |"
sep = "| --- | " + " | ".join("---:" for _ in period_order) + " |"
lines += [hdr, sep]
for k in key_terms:
    cells = []
    for p in period_order:
        a = agg.get(p)
        v = round(a[k] / a["words"] * 10000, 3) if a and a["words"] else 0
        cells.append(f"{v:g}")
    lines.append(f"| {k} | " + " | ".join(cells) + " |")
lines += ["", "## Volumes & words per period", "",
          "| period | volumes | words |", "| --- | ---: | ---: |"]
for p in period_order:
    a = agg.get(p)
    if a:
        lines.append(f"| {p} | {a['volumes']} | {a['words']:,} |")
(OUT / "term_drift_summary_1942_2019.md").write_text("\n".join(lines) + "\n")

print(f"volumes processed: {len(rows)}; periods: {period_order}")
print((OUT / 'term_drift_summary_1942_2019.md').read_text())

# Generates the two figures for RTR-WP-008. Do not hand-edit the PNGs.
# Run: .venv/bin/python research/working-papers/RTR-WP-008-ila-discourse/analysis/make_figures.py
# fig1 term-drift reads the corpus CSV; fig2 timeline encodes the documented
# committee chain (sources cited in the paper body + Compendium).

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[4]
CSV = ROOT / "data" / "ila-conference-proceedings" / "analysis" / "term_drift_by_period_1942_2019.csv"
FIGDIR = Path(__file__).resolve().parents[1] / "paper" / "figures"
FIGDIR.mkdir(parents=True, exist_ok=True)

INK = "#1a1a1a"
RED = "#b3202a"
GREY = "#8a8a8a"

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9,
    "axes.edgecolor": INK,
    "axes.linewidth": 0.6,
    "figure.dpi": 200,
})


def fig_term_drift():
    df = pd.read_csv(CSV)
    periods = list(dict.fromkeys(df["period"]))  # preserve order
    x = range(len(periods))

    def series(term):
        d = df[df["term"] == term].set_index("period")["per_10k_words"]
        return [d.get(p, 0.0) for p in periods]

    # `information` peaks at 136 and would flatten everything; held out, noted in caption.
    lines = [
        ("reader", INK, "-", "reader"),
        ("user", RED, "-", "user"),
        ("public_library", INK, "--", "public library"),
        ("digital", GREY, "-", "digital"),
        ("caste", RED, ":", "caste"),
    ]

    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    for term, colour, style, label in lines:
        y = series(term)
        ax.plot(x, y, style, color=colour, linewidth=1.6 if term in ("user", "public_library") else 1.1,
                marker="o", markersize=2.5, label=label)

    ax.set_xticks(list(x))
    ax.set_xticklabels([p.replace("-", "–") for p in periods], rotation=0, fontsize=7.5)
    ax.set_ylabel("occurrences per 10,000 words")
    ax.set_ylim(bottom=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, fontsize=7.5, loc="upper left", ncol=2)
    # mark the reader/user crossover (between 1950-69 and 1970-85)
    ax.annotate("reader / user\ncrossover", xy=(2, 13), xytext=(1.15, 30),
                fontsize=6.8, color=RED, ha="left",
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.7))
    fig.tight_layout()
    out = FIGDIR / "fig1_term_drift.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_timeline():
    # (year, short label, kind): demand/recommendation vs refusal/deferral/inversion
    events = [
        (1936, "Bombay Bill No. XXIV\nintroduced, not considered", "refusal"),
        (1939, "Library Development Cttee\ncess declined; permissive only", "refusal"),
        (1944, "ILA: central, mandatory,\ntax-funded, free demanded", "demand"),
        (1957, "Sinha Cttee: free access a\nfundamental right; cess; 20-yr clause", "demand"),
        (1966, "Fourth Plan WG:\nRs 30.99 cr + Draft Bill", "demand"),
        (1986, "NAPLIS drafted,\nnever laid before Parliament", "refusal"),
        (1993, "pared to Re.1–Rs.10 fee;\n“State subject”", "refusal"),
        (2011, "“wait for a PIL\nin the Supreme Court?”", "refusal"),
        (2025, "“no such data …\nno such plan”", "refusal"),
    ]
    # Events are spaced evenly (sequence is the point, not exact gaps); the real
    # year is the bold label. Clustered early dates would otherwise collide.
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.axhline(0, color=INK, lw=1.0, zorder=1)
    xs = list(range(len(events)))
    for x, (yr, label, kind) in zip(xs, events):
        up = x % 2 == 0
        y = 1 if up else -1
        colour = RED if kind == "refusal" else INK
        filled = kind == "demand"
        ax.plot([x], [0], marker="o", markersize=5,
                markerfacecolor=(INK if filled else "white"),
                markeredgecolor=colour, markeredgewidth=1.2, zorder=3)
        ax.plot([x, x], [0, y * 0.45], color=colour, lw=0.7, zorder=2)
        ax.text(x, y * 0.52, f"{yr}", ha="center",
                va="bottom" if up else "top", fontsize=8, color=colour, fontweight="bold")
        ax.text(x, y * 0.52 + (0.18 if up else -0.18), label, ha="center",
                va="bottom" if up else "top", fontsize=6.4, color=INK)

    ax.set_xlim(-0.6, len(events) - 0.4)
    ax.set_ylim(-1.7, 1.7)
    ax.axis("off")
    legend = [
        Line2D([0], [0], marker="o", color="white", markerfacecolor=INK,
               markeredgecolor=INK, markersize=6, label="demand / recommendation"),
        Line2D([0], [0], marker="o", color="white", markerfacecolor="white",
               markeredgecolor=RED, markeredgewidth=1.2, markersize=6, label="refusal / deferral / inversion"),
    ]
    ax.legend(handles=legend, frameon=False, fontsize=6.8, loc="lower center",
              ncol=2, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout()
    out = FIGDIR / "fig2_deferral_timeline.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    print("wrote", fig_term_drift())
    print("wrote", fig_timeline())

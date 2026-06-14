#!/usr/bin/env python3
"""Generate figures for the Ahmedabad/Toronto public-library comparison paper.

Outputs PNGs into docs/figures/. All numbers are read from the same source
tables the paper cites, so the figures are reproducible and provenance-clean:

  - data/cities/ahmedabad/source/libraries/mj_library_annual_stats.csv
  - data/cities/ahmedabad/source/libraries/mj_library_finance.csv
  - data/cities/ahmedabad/layers/wards.geojson
  - data/cities/ahmedabad/derived/library_access/origin_travel_times.csv
  - data/cities/ahmedabad/source/libraries/ahmedabad_library_locations.csv

Run: .venv/bin/python3 scripts/make_library_paper_figures.py
"""
from __future__ import annotations

import pathlib

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIG = ROOT / "paper" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# Atlas palette (matches the Quarto header definitions).
INK = "#172126"
BLUE = "#1B4E6B"
MUTED = "#66737A"
RULE = "#D6DEE2"
ALERT = "#B0412B"      # brick — used for the failing / starved series
TEAL = "#6FA8C7"       # secondary cool
PAPER = "#FFFFFF"

mpl.rcParams.update({
    "font.family": "Helvetica",
    "font.size": 10.5,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "axes.titlecolor": INK,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.linewidth": 0.8,
    "figure.facecolor": PAPER,
    "axes.facecolor": PAPER,
    "savefig.facecolor": PAPER,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
})


def _thousands(x, _pos):
    return f"{x:,.0f}"


def _despine(ax, keep=("left", "bottom")):
    for side, spine in ax.spines.items():
        spine.set_visible(side in keep)


def fig_decline():
    """Hero figure: circulation and active-membership decline, 2015-16 to 2025-26."""
    df = pd.read_csv(ROOT / "data/cities/ahmedabad/source/libraries/mj_library_annual_stats.csv")
    df = df.sort_values("year")
    yr = df["year"].tolist()
    x = range(len(yr))

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(8.0, 6.2), sharex=True, gridspec_kw={"hspace": 0.18}
    )

    # COVID band on both panels.
    covid = [i for i, y in enumerate(yr) if y in ("2020-21", "2021-22")]
    for ax in (ax1, ax2):
        ax.axvspan(min(covid) - 0.5, max(covid) + 0.5, color=RULE, alpha=0.55, zorder=0)

    # Panel 1: circulation.
    circ = df["circulation_total"]
    ax1.plot(x, circ, color=BLUE, lw=2.2, marker="o", ms=5, zorder=3)
    pk = circ.idxmax()
    pk_i = list(df.index).index(pk)
    ax1.annotate(
        f"peak {circ.loc[pk]:,}\n({yr[pk_i]})",
        xy=(pk_i, circ.loc[pk]), xytext=(pk_i + 0.3, circ.loc[pk] + 8000),
        color=BLUE, fontsize=8.5,
    )
    last = len(yr) - 1
    drop = (circ.iloc[-1] - circ.loc[pk]) / circ.loc[pk] * 100
    ax1.annotate(
        f"{circ.iloc[-1]:,}\n({drop:+.0f}% vs peak)",
        xy=(last, circ.iloc[-1]), xytext=(last - 1.7, circ.iloc[-1] - 42000),
        color=ALERT, fontsize=8.5,
        arrowprops=dict(arrowstyle="-", color=ALERT, lw=0.8),
    )
    ax1.set_ylabel("Annual circulation")
    ax1.yaxis.set_major_formatter(FuncFormatter(_thousands))
    ax1.set_ylim(0, 240000)
    ax1.set_title("Use is falling: M.J. Library Network, 2015–16 to 2025–26",
                  loc="left", fontweight="bold", fontsize=12.5, pad=8)
    _despine(ax1)

    # Panel 2: annual active members.
    ann = df["annual_members"]
    ax2.plot(x, ann, color=ALERT, lw=2.2, marker="o", ms=5, zorder=3)
    apk = ann.idxmax()
    apk_i = list(df.index).index(apk)
    ax2.annotate(
        f"peak {int(ann.loc[apk]):,} ({yr[apk_i]})",
        xy=(apk_i, ann.loc[apk]), xytext=(apk_i - 0.2, ann.loc[apk] + 250),
        color=INK, fontsize=8.5,
    )
    atr = ann.idxmin()
    atr_i = list(df.index).index(atr)
    ax2.annotate(
        f"trough {int(ann.loc[atr]):,}",
        xy=(atr_i, ann.loc[atr]), xytext=(atr_i + 0.2, ann.loc[atr] + 430),
        color=ALERT, fontsize=8.5, ha="left",
    )
    ax2.set_ylabel("New annual\n(active) members")
    ax2.set_ylim(0, 3700)
    _despine(ax2)

    ax2.set_xticks(list(x))
    ax2.set_xticklabels(yr, rotation=45, ha="right", fontsize=8.5)
    fig.text(0.0, -0.02,
             "Source: M.J. Library Network annual proactive disclosures (RTI). "
             "Shaded band = 2020–22 (COVID).",
             fontsize=7.5, color=MUTED)
    fig.savefig(FIG / "fig1_decade_decline.png")
    plt.close(fig)
    print("wrote fig1_decade_decline.png")


def fig_membership_roll():
    """Lifetime roll keeps growing while the active sliver vanishes."""
    df = pd.read_csv(ROOT / "data/cities/ahmedabad/source/libraries/mj_library_annual_stats.csv")
    df = df.sort_values("year")
    yr = df["year"].tolist()
    x = range(len(yr))
    life = df["lifetime_members"]
    ann = df["annual_members"]

    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    ax.bar(x, life, color=MUTED, width=0.66, label="Lifetime members (never expire)")
    ax.bar(x, ann, bottom=life, color=ALERT, width=0.66, label="Annual (active) members")

    # Active share callouts at first and last year.
    for i in (0, len(yr) - 1):
        tot = life.iloc[i] + ann.iloc[i]
        share = ann.iloc[i] / tot * 100
        ax.annotate(f"active {share:.0f}%" if i == 0 else f"active {share:.1f}%",
                    xy=(i, tot), xytext=(i, tot + 1400),
                    ha="center", fontsize=8.5, color=ALERT)

    ax.set_ylabel("Members on the roll")
    ax.yaxis.set_major_formatter(FuncFormatter(_thousands))
    ax.set_ylim(0, 31000)
    ax.set_xticks(list(x))
    ax.set_xticklabels(yr, rotation=45, ha="right", fontsize=8.5)
    ax.set_title("A roll, not a public: the total holds only because lifetime members never leave",
                 loc="left", fontweight="bold", fontsize=11.5, pad=8)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    _despine(ax)
    fig.text(0.0, -0.04,
             "Source: M.J. Library Network annual proactive disclosures (RTI). "
             "Gyanvihar branch members excluded for a clean lifetime/annual split.",
             fontsize=7.5, color=MUTED)
    fig.savefig(FIG / "fig2_membership_roll.png")
    plt.close(fig)
    print("wrote fig2_membership_roll.png")


def fig_budget():
    """2025-26 budget composition: establishment dominates, books are starved."""
    fin = pd.read_csv(ROOT / "data/cities/ahmedabad/source/libraries/mj_library_finance.csv")
    row = fin[fin["year"] == "2025-26"].iloc[0]
    total = row["total_budget_cr"]
    items = [
        ("Establishment / payroll", row["establishment_payroll_cr"]),
        ("New plans (unallocated)", row["new_plans_cr"]),
        ("Library service", row["library_service_cr"]),
        ("Capital", row["capital_cr"]),
        ("Maintenance", row["maintenance_cr"]),
        ("IT / automation", row["it_automation_cr"]),
        ("Reading material", row["reading_material_cr"]),
        ("Administration", row["administration_cr"]),
        ("Miscellaneous", row["miscellaneous_cr"]),
    ]
    items.sort(key=lambda kv: kv[1])  # ascending so largest bar is on top
    labels = [k for k, _ in items]
    vals = [v for _, v in items]
    shares = [v / total * 100 for v in vals]
    colors = [ALERT if k == "Reading material" else
              (BLUE if k == "Establishment / payroll" else MUTED) for k in labels]

    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    y = range(len(labels))
    ax.barh(list(y), shares, color=colors, height=0.66)
    for i, (s, v) in enumerate(zip(shares, vals)):
        ax.text(s + 0.8, i, f"{s:.1f}%  (₹{v:.2f} cr)", va="center", fontsize=8.5,
                color=INK if labels[i] in ("Reading material", "Establishment / payroll") else MUTED)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlim(0, 72)
    ax.set_xlabel("Share of 2025–26 budget (%)")
    ax.set_title("Two-thirds to establishment, 1.4% to books",
                 loc="left", fontweight="bold", fontsize=12.5, pad=8)
    _despine(ax, keep=("bottom",))
    ax.tick_params(left=False)
    fig.text(0.0, -0.04,
             "Source: M.J. Library Network 2025–26 budget disclosure. "
             "Total ₹22.77 cr. ‘New plans’ is disclosed as a lump, not by category.",
             fontsize=7.5, color=MUTED)
    fig.savefig(FIG / "fig3_budget_composition.png")
    plt.close(fig)
    print("wrote fig3_budget_composition.png")


def fig_access_map():
    """Choropleth: ward-centroid walk minutes to nearest library, with library points."""
    wards = gpd.read_file(ROOT / "data/cities/ahmedabad/layers/wards.geojson")
    times = pd.read_csv(ROOT / "data/cities/ahmedabad/derived/library_access/origin_travel_times.csv")
    libs = pd.read_csv(ROOT / "data/cities/ahmedabad/source/libraries/ahmedabad_library_locations.csv")

    wards["ward_no"] = wards["ward_no"].astype(int)
    times["ward_no"] = times["ward_no"].astype(int)
    g = wards.merge(
        times[["ward_no", "ward_name", "walk_minutes_to_nearest_library", "population"]],
        on="ward_no", how="left",
    )

    fig, ax = plt.subplots(figsize=(7.6, 8.0))
    g.plot(
        column="walk_minutes_to_nearest_library", cmap="YlOrRd", linewidth=0.5,
        edgecolor="white", ax=ax, legend=True,
        legend_kwds={"label": "Walk minutes to nearest library (ward centroid)",
                     "shrink": 0.55, "orientation": "horizontal", "pad": 0.02},
    )
    ax.scatter(libs["longitude"], libs["latitude"], s=11, color=INK,
               edgecolor="white", linewidth=0.3, zorder=5, label="Library locations (83)")

    # Label the worst-served wards.
    worst = g.sort_values("walk_minutes_to_nearest_library", ascending=False).head(5)
    for _, r in worst.iterrows():
        c = r.geometry.representative_point()
        name = str(r["ward_name"]).split(" ", 1)[-1].title()
        ax.annotate(f"{name}\n{r['walk_minutes_to_nearest_library']:.0f} min",
                    xy=(c.x, c.y), ha="center", va="center", fontsize=7.5,
                    color=INK, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.7))

    ax.set_title("Ahmedabad: ward-centroid walk time to the nearest library",
                 loc="left", fontweight="bold", fontsize=12.5, pad=8)
    ax.set_axis_off()
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    fig.text(0.01, 0.02,
             "Source: Right 2 Read Campaign ward-centroid access proxy (48 AMC wards, 83 library "
             "locations). Proxy, not scheduled-transit routing; understates within-ward inequality.",
             fontsize=7.5, color=MUTED)
    fig.savefig(FIG / "fig4_access_map.png")
    plt.close(fig)
    print("wrote fig4_access_map.png")


def fig_transit_map():
    """Metro and BRTS reach the periphery; libraries don't.

    Ward fill = walk minutes to nearest library (same scale as Figure 4).
    Overlaid: AMTS bus corridors (faint), Janmarg/AJL BRTS corridors, Metro
    lines, and the 83 library locations split by whether they sit within 500 m
    of a rapid (Metro or BRTS) corridor. The point: the rapid-transit network
    already runs through the worst-served wards, but libraries are not sited on it.
    """
    import numpy as np
    METRO = "#7B2D8E"   # purple
    NEAR = "#1f9e6b"    # green — library near rapid transit
    M = 32643  # UTM 43N, metres — for distance work
    wards = gpd.read_file(ROOT / "data/cities/ahmedabad/layers/wards.geojson").to_crs(M)
    times = pd.read_csv(ROOT / "data/cities/ahmedabad/derived/library_access/origin_travel_times.csv")
    libs = pd.read_csv(ROOT / "data/cities/ahmedabad/source/libraries/ahmedabad_library_locations.csv")
    brts = gpd.read_file(ROOT / "data/cities/ahmedabad/layers/corr_brts.geojson").to_crs(M)
    amts = gpd.read_file(ROOT / "data/cities/ahmedabad/layers/corr_amts.geojson").to_crs(M)
    metro = gpd.read_file(ROOT / "data/cities/ahmedabad/layers/metro_lines.geojson").to_crs(M)

    wards["ward_no"] = wards["ward_no"].astype(int)
    times["ward_no"] = times["ward_no"].astype(int)
    g = wards.merge(
        times[["ward_no", "ward_name", "walk_minutes_to_nearest_library"]],
        on="ward_no", how="left",
    )
    lg = gpd.GeoDataFrame(
        libs, geometry=gpd.points_from_xy(libs.longitude, libs.latitude), crs=4326
    ).to_crs(M)
    lg["d_rapid"] = np.minimum(
        lg.geometry.distance(brts.union_all()),
        lg.geometry.distance(metro.union_all()),
    )
    near = lg["d_rapid"] <= 500
    n_near = int(near.sum())

    fig, ax = plt.subplots(figsize=(7.6, 8.0))
    g.plot(
        column="walk_minutes_to_nearest_library", cmap="YlOrRd", linewidth=0.5,
        edgecolor="white", ax=ax, alpha=0.90, legend=True,
        legend_kwds={"label": "Walk minutes to nearest library (ward centroid)",
                     "shrink": 0.55, "orientation": "horizontal", "pad": 0.02},
    )
    amts.plot(ax=ax, color=MUTED, linewidth=0.4, alpha=0.40, zorder=3)
    brts.plot(ax=ax, color=BLUE, linewidth=2.0, alpha=0.95, zorder=4)
    metro.plot(ax=ax, color=METRO, linewidth=2.0, alpha=0.95, zorder=5)
    lg[~near].plot(ax=ax, color=INK, markersize=14, marker="o",
                   edgecolor="white", linewidth=0.3, zorder=6)
    lg[near].plot(ax=ax, color=NEAR, markersize=18, marker="o",
                  edgecolor="white", linewidth=0.4, zorder=7)

    # Label the worst-served wards (Metro and/or BRTS runs through every one).
    worst = g.sort_values("walk_minutes_to_nearest_library", ascending=False).head(5)
    for _, r in worst.iterrows():
        c = r.geometry.representative_point()
        name = str(r["ward_name"]).split(" ", 1)[-1].title()
        ax.annotate(f"{name}\n{r['walk_minutes_to_nearest_library']:.0f} min walk",
                    xy=(c.x, c.y), ha="center", va="center", fontsize=7.5,
                    color=INK, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.72))

    from matplotlib.lines import Line2D
    handles = [
        Line2D([0], [0], color=METRO, lw=2.0, label="Metro line"),
        Line2D([0], [0], color=BLUE, lw=2.0, label="Janmarg / AJL BRTS corridor"),
        Line2D([0], [0], color=MUTED, lw=0.8, alpha=0.6, label="AMTS bus corridor"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=NEAR,
               markeredgecolor="white", markersize=8,
               label=f"Library ≤500 m from rapid transit ({n_near})"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=INK,
               markeredgecolor="white", markersize=8,
               label=f"Library >500 m from rapid transit ({len(lg) - n_near})"),
    ]
    ax.legend(handles=handles, frameon=False, fontsize=7.8, loc="lower left")

    ax.set_title("Metro and BRTS reach the periphery; libraries do not",
                 loc="left", fontweight="bold", fontsize=12.5, pad=8)
    ax.set_axis_off()
    fig.text(0.01, 0.02,
             "Sources: Metro, Janmarg/AJL BRTS and AMTS corridor geometry (AMC/GMRC/GTFS); Right 2 Read "
             "Campaign ward walk-access proxy. A Metro or BRTS corridor runs through every labelled worst-served ward.",
             fontsize=7.3, color=MUTED)
    fig.savefig(FIG / "fig5_transit_map.png")
    plt.close(fig)
    print(f"wrote fig5_transit_map.png ({n_near}/{len(lg)} libraries within 500 m of Metro/BRTS)")


if __name__ == "__main__":
    fig_decline()
    fig_membership_roll()
    fig_budget()
    fig_access_map()
    fig_transit_map()
    print("All figures written to", FIG)

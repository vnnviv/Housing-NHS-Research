"""Figures for the NHS brief. Run from the repo root: python analysis/make_figures.py

Palette: reference categorical slots 1-2 (blue, orange), validated for light mode.
Two series are direct-labeled; caps are labeled on the lines, not in a legend alone.
"""
import sys
from dataclasses import replace
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cap_sensitivity as cs          # noqa: E402
import downpayment_scenarios as dps   # noqa: E402

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9"
BLUE, ORANGE = "#2a78d6", "#eb6834"
OUT = Path(__file__).resolve().parent.parent / "figures"


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#c3c2b7")
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def money_k(x, _):
    return f"${x / 1000:,.0f}k"


def main():
    rows = dps.load_rows()
    bench = dps.price_benchmark(rows)
    p = cs.Params(rate=0.0740)
    Rs = [0, 25_000, 50_000, 75_000, 100_000, 125_000, 150_000]
    OUT.mkdir(exist_ok=True)

    # Figure 1: required income vs principal reduction, with the caps
    fig, ax = plt.subplots(figsize=(7.2, 4.4), facecolor=SURFACE)
    style(ax)
    for price, color, name, dy in ((bench["p25"], BLUE, "25th pct at 30% ratio", 8_000),
                                   (bench["p50"], ORANGE, "Median home", 4_000)):
        ys = [cs.required_income(price, p, r) for r in Rs]
        ax.plot(Rs, ys, color=color, linewidth=2)
        ax.text(Rs[-1] + 2500, ys[-1] + dy, f"{name}\n${price / 1000:,.0f}k" if name == "Median home" else f"{name}\n${price / 1000:,.0f}k home", color=INK,
                fontsize=9, va="center")
    ys43 = [cs.required_income(bench["p25"], replace(p, housing_dti=0.43), r) for r in Rs]
    ax.plot(Rs, ys43, color=BLUE, linewidth=2, linestyle=(0, (5, 3)))
    ax.text(Rs[-1] + 2500, ys43[-1] + 4_000, "25th pct at 43% ratio", color=INK, fontsize=9, va="center")
    for name, cap in (("HUD low = HCD moderate  $133k", 133_250), ("HUD very low  $83k", 83_300)):
        ax.axhline(cap, color=MUTED, linewidth=1, linestyle=(0, (4, 3)))
        ax.text(105_000 if cap > 100_000 else 0, cap - 9_000 if cap > 100_000 else cap + 3000, name, color=MUTED, fontsize=8.5)
    ax.set_xlim(0, 195_000)
    ax.set_ylim(60_000, 240_000)
    ax.xaxis.set_major_formatter(money_k)
    ax.yaxis.set_major_formatter(money_k)
    ax.set_xlabel("Principal reduction from soft assistance", color=MUTED, fontsize=9)
    ax.set_ylabel("Income needed for the first mortgage", color=MUTED, fontsize=9)
    ax.set_title("Income a Compton home requires vs the caps, at two housing ratios (7.40%)",
                 loc="left", color=INK, fontsize=10.5)
    fig.text(0.01, 0.045, "Exploratory. Price = Assessor base-year value on 2025-26 resets, not recorded sales.",
             color=MUTED, fontsize=7.5)
    fig.text(0.01, 0.01, "Cash needs assumed met. The slope changes once the loan falls below 80% of price "
             "(mortgage insurance ends).", color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(OUT / "fig1_required_income.png", dpi=200, facecolor=SURFACE)
    plt.close(fig)

    # Figure 2: tornado
    t = cs.tornado(bench["p25"], p, 0.0)
    t = [r for r in t if r["swing"] > 0]
    labels = {"rate": "Mortgage rate 5.98-7.79%", "price_mult": "Price proxy x0.95-1.10",
              "mi_scale": "Mortgage insurance x0.59-1.67", "insurance_monthly": "Insurance $100-300/mo",
              "tax_rate": "Property tax 1.00-1.25%"}
    t = sorted(t, key=lambda r: r["swing"])
    fig, ax = plt.subplots(figsize=(7.2, 3.4), facecolor=SURFACE)
    style(ax)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.grid(axis="y", visible=False)
    ys = range(len(t))
    ax.barh(list(ys), [r["swing"] for r in t], color=BLUE, height=0.55)
    for i, r in zip(ys, t):
        ax.text(r["swing"] + 400, i, f"${r['swing']:,.0f}", va="center", color=INK, fontsize=9)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([labels.get(r["axis"], r["axis"]) for r in t], color=INK, fontsize=9)
    ax.xaxis.set_major_formatter(money_k)
    ax.set_xlim(0, max(r["swing"] for r in t) * 1.2)
    ax.set_title("What moves required income most (25th-percentile home)",
                 loc="left", color=INK, fontsize=10.5)
    ax.set_xlabel("Swing in required income across the range", color=MUTED, fontsize=9)
    fig.text(0.01, 0.01, "Ranges: rate sourced (PMMS 2023-26); others are placeholders.",
             color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(OUT / "fig2_tornado.png", dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print("wrote", *sorted(p.name for p in OUT.glob("*.png")))


if __name__ == "__main__":
    main()

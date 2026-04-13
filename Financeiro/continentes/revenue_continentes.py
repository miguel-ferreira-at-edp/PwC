"""
Revenue por Continente/Região — evolução anual.
Gera 3 ficheiros separados:
  _abs.png   → Stacked Area volume absoluto
  _pct.png   → Stacked Area 100% (quota global)
  _stats.png → Tabela de estatísticas acumuladas
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "..", "..", "data", "sales_data_clean.csv")
OUTPUT_DIR = BASE_DIR

# ── Load & prepare ─────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
df["Revenue"] = df["Sales_Price"]

region_revenue = (
    df.groupby(["Year", "Region"])["Revenue"]
    .sum()
    .reset_index()
    .sort_values(["Year", "Region"])
)

pivot = (
    region_revenue
    .pivot(index="Year", columns="Region", values="Revenue")
    .fillna(0)
)

col_order = pivot.sum().sort_values(ascending=False).index.tolist()
pivot     = pivot[col_order]
years     = pivot.index.tolist()
regions   = pivot.columns.tolist()
n_years   = len(years)

COLORS = {
    "Asia":          "#4e9af1",
    "Europe":        "#f4a02a",
    "North America": "#3cba54",
}
LABELS = {
    "Asia":          "Ásia",
    "Europe":        "Europa",
    "North America": "América do Norte",
}

def cagr(series):
    v0, vn = series.iloc[0], series.iloc[-1]
    if v0 <= 0:
        return float("nan")
    return ((vn / v0) ** (1 / (n_years - 1)) - 1) * 100

# ── Estatísticas ───────────────────────────────────────────────────────────────
stats = {}
for r in regions:
    s = pivot[r]
    stats[r] = {
        "total":    s.sum(),
        "media":    s.mean(),
        "cagr":     cagr(s),
        "yoy_mean": s.pct_change().mean() * 100,
        "pico_ano": years[s.argmax()],
        "pico_val": s.max(),
        "min_ano":  years[s.argmin()],
        "min_val":  s.min(),
    }

total_per_year = pivot[regions].sum(axis=1)
cumsum         = pivot[regions].cumsum(axis=1)
pivot_pct      = pivot[regions].div(total_per_year, axis=0) * 100
cumsum_pct     = pivot_pct.cumsum(axis=1)

vals     = [pivot[r].values   for r in regions]
vals_pct = [pivot_pct[r].values for r in regions]
colors   = [COLORS[r]         for r in regions]
labels   = [LABELS[r]         for r in regions]

MIN_FRAC     = 0.04
FRAC_NORMAL  = 0.13
FONT_SMALL   = 6.0
FONT_NORMAL  = 8.5
PCT_SMALL_MIN  = 4
PCT_NORMAL     = 10
FONT_PCT_SMALL  = 6.0
FONT_PCT_NORMAL = 9.0

# ────────────────────────────────────────────────────────────────────────────────
# PNG 1 — Volume Absoluto
# ────────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 7))
fig.suptitle(
    "Revenue por Região — Evolução Anual (2020–2025)\nVolume Absoluto",
    fontsize=13, fontweight="bold",
)

ax.stackplot(years, vals, labels=labels, colors=colors, alpha=0.85)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e6:.1f}M"))
ax.set_xlim(years[0] - 0.3, years[-1] + 0.3)
ax.set_xticks(years)
ax.tick_params(axis="x", labelsize=11)
ax.set_xlabel("Ano", fontsize=11)
ax.set_ylabel("Revenue", fontsize=11)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22),
          ncol=3, fontsize=10, framealpha=0.85)
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.margins(y=0.15)

# Total no topo, ano a ano
for yr, tot in zip(years, total_per_year):
    ax.annotate(
        f"${tot/1e6:.1f}M",
        xy=(yr, tot),
        xytext=(0, 10), textcoords="offset points",
        ha="center", va="bottom",
        fontsize=9, color="#111111", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                  edgecolor="#cccccc", alpha=0.85),
    )

# Valor dentro de cada banda, ano a ano
for region in regions:
    for yr, tot_yr in zip(years, total_per_year):
        val  = pivot[region].loc[yr]
        frac = val / tot_yr
        if frac < MIN_FRAC:
            continue
        y_mid = cumsum[region].loc[yr] - val / 2
        fs = FONT_NORMAL if frac >= FRAC_NORMAL else FONT_SMALL
        ax.text(yr, y_mid, f"${val/1e6:.1f}M",
                ha="center", va="center",
                fontsize=fs, color="black", fontweight="bold")

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "revenue_continentes_abs.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

# ────────────────────────────────────────────────────────────────────────────────
# PNG 2 — Quota Relativa 100% Stacked
# ────────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 7))
fig.suptitle(
    "Revenue por Região — Evolução Anual (2020–2025)\nQuota Relativa Global — 100% Stacked",
    fontsize=13, fontweight="bold",
)

ax.stackplot(years, vals_pct, labels=labels, colors=colors, alpha=0.85)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.set_xlim(years[0] - 0.3, years[-1] + 0.3)
ax.set_xticks(years)
ax.tick_params(axis="x", labelsize=11)
ax.set_ylim(0, 110)
ax.set_xlabel("Ano", fontsize=11)
ax.set_ylabel("Quota de Revenue (%)", fontsize=11)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22),
          ncol=3, fontsize=10, framealpha=0.85)
ax.grid(axis="y", linestyle="--", alpha=0.35)

for region in regions:
    for yr in years:
        pct = pivot_pct[region].loc[yr]
        if pct < PCT_SMALL_MIN:
            continue
        y_mid = cumsum_pct[region].loc[yr] - pct / 2
        fs = FONT_PCT_NORMAL if pct >= PCT_NORMAL else FONT_PCT_SMALL
        ax.text(yr, y_mid, f"{pct:.1f}%",
                ha="center", va="center",
                fontsize=fs, color="black", fontweight="bold")

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "revenue_continentes_pct.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

# ────────────────────────────────────────────────────────────────────────────────
# PNG 3 — Tabela de estatísticas
# ────────────────────────────────────────────────────────────────────────────────
row_labels = [
    "Revenue Total Acum.",
    "Média Anual",
    "CAGR",
    "Cresc. Médio YoY",
    "Pico (ano)",
    "Mínimo (ano)",
]
cell_data = [
    [f"${stats[r]['total']/1e6:.1f}M"                                  for r in regions],
    [f"${stats[r]['media']/1e6:.2f}M"                                  for r in regions],
    [f"{stats[r]['cagr']:.1f}%"                                        for r in regions],
    [f"{stats[r]['yoy_mean']:.1f}%"                                    for r in regions],
    [f"${stats[r]['pico_val']/1e6:.1f}M  ({stats[r]['pico_ano']})"    for r in regions],
    [f"${stats[r]['min_val']/1e6:.1f}M  ({stats[r]['min_ano']})"      for r in regions],
]

n_rows = len(row_labels)
fig_h  = 1.2 + n_rows * 0.55 + 0.6
fig, ax = plt.subplots(figsize=(12, fig_h))
ax.axis("off")
fig.suptitle("Estatísticas Acumuladas por Região", fontsize=13,
             fontweight="bold", y=0.97)

tbl = ax.table(
    cellText=cell_data,
    rowLabels=row_labels,
    colLabels=[LABELS[r] for r in regions],
    cellLoc="center",
    rowLoc="left",
    loc="center",
    bbox=[0.0, 0.0, 1.0, 0.92],
    colWidths=[0.28] + [0.72 / len(regions)] * len(regions),
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(10.5)

for j, region in enumerate(regions):
    cell = tbl[(0, j)]
    cell.set_facecolor(COLORS[region])
    cell.set_text_props(color="white", fontweight="bold")
    cell.set_edgecolor("#bbbbbb")
    cell.set_height(0.14)

for i in range(n_rows):
    tbl[(i + 1, -1)].set_facecolor("#e8e8e8")
    tbl[(i + 1, -1)].set_text_props(fontweight="bold")
    tbl[(i + 1, -1)].set_edgecolor("#bbbbbb")
    tbl[(i + 1, -1)].set_height(0.12)
    for j in range(len(regions)):
        cell = tbl[(i + 1, j)]
        cell.set_facecolor("#f7f7f7" if i % 2 == 0 else "#ffffff")
        cell.set_edgecolor("#bbbbbb")
        cell.set_height(0.12)

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "revenue_continentes_stats.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

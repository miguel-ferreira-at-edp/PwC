"""
F06 — Production Cost Ratio por Continente/Região
SUM(Production_Cost) / SUM(Sales_Price) × 100

Gera 2 ficheiros:
  _bars.png   → Barras agrupadas por ano
  _stats.png  → Tabela de estatísticas acumuladas
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "..", "..", "data", "sales_data_clean.csv")
OUTPUT_DIR = BASE_DIR

# ── Load & prepare ─────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)

region_annual = (
    df.groupby(["Year", "Region"])
    .agg(Production_Cost=("Production_Cost", "sum"),
         Sales_Price=("Sales_Price", "sum"))
    .reset_index()
)
region_annual["PCR"] = region_annual["Production_Cost"] / region_annual["Sales_Price"] * 100

pivot = (
    region_annual.pivot(index="Year", columns="Region", values="PCR")
    .fillna(0)
)

col_order = pivot.mean().sort_values(ascending=False).index.tolist()
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

# ── Estatísticas ───────────────────────────────────────────────────────────────
stats = {}
for r in regions:
    s = pivot[r]
    yoy = s.diff()
    stats[r] = {
        "media":      s.mean(),
        "min_val":    s.min(),
        "min_ano":    years[s.argmin()],
        "max_val":    s.max(),
        "max_ano":    years[s.argmax()],
        "variacao":   s.iloc[-1] - s.iloc[0],
        "yoy_mean":   yoy.mean(),
        "yoy_best":   yoy.min(),
        "yoy_best_yr": yoy.idxmin(),
    }

# ────────────────────────────────────────────────────────────────────────────────
# PNG 1 — Barras agrupadas por ano
# ────────────────────────────────────────────────────────────────────────────────
n_regions = len(regions)
x         = np.arange(len(years))
width     = 0.22
offsets   = np.linspace(-(n_regions - 1) / 2, (n_regions - 1) / 2, n_regions) * width

fig, ax = plt.subplots(figsize=(14, 7))
fig.suptitle(
    "Production Cost Ratio por Região — Barras Agrupadas (2020–2025)",
    fontsize=13, fontweight="bold",
)

for i, r in enumerate(regions):
    bars = ax.bar(
        x + offsets[i], pivot[r].values,
        width=width, color=COLORS[r], alpha=0.82,
        label=LABELS[r],
    )
    for bar, val in zip(bars, pivot[r].values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.15,
            f"{val:.1f}%",
            ha="center", va="bottom", fontsize=7.5, color=COLORS[r], fontweight="bold",
        )

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
ax.set_xticks(x)
ax.set_xticklabels(years, fontsize=11)
ax.set_xlabel("Ano", fontsize=11)
ax.set_ylabel("Production Cost Ratio (%)", fontsize=11)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.18),
          ncol=3, fontsize=10, framealpha=0.85)
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.margins(y=0.12)

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "production_cost_ratio_continentes_bars.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

# ────────────────────────────────────────────────────────────────────────────────
# PNG 2 — Tabela de estatísticas
# ────────────────────────────────────────────────────────────────────────────────
row_labels = [
    "PCR Médio (período)",
    "PCR Mínimo (ano)",
    "PCR Máximo (ano)",
    "Variação Total (pp)",
    "Var. Média YoY (pp)",
    "Melhor Ano (↓ custo)",
]
cell_data = [
    [f"{stats[r]['media']:.1f}%"                                              for r in regions],
    [f"{stats[r]['min_val']:.1f}%  ({stats[r]['min_ano']})"                   for r in regions],
    [f"{stats[r]['max_val']:.1f}%  ({stats[r]['max_ano']})"                   for r in regions],
    [f"{stats[r]['variacao']:+.1f} pp"                                        for r in regions],
    [f"{stats[r]['yoy_mean']:+.1f} pp"                                        for r in regions],
    [f"{stats[r]['yoy_best_yr']} ({stats[r]['yoy_best']:+.1f} pp)"           for r in regions],
]

n_rows = len(row_labels)
fig_h  = 1.2 + n_rows * 0.55 + 0.6
fig, ax = plt.subplots(figsize=(12, fig_h))
ax.axis("off")
fig.suptitle("Estatísticas Acumuladas — Production Cost Ratio por Região",
             fontsize=13, fontweight="bold", y=0.97)

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

for j, r in enumerate(regions):
    cell = tbl[(0, j)]
    cell.set_facecolor(COLORS[r])
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
p = os.path.join(OUTPUT_DIR, "production_cost_ratio_continentes_stats.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

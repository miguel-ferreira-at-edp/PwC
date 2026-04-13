"""
F07 — YoY Revenue Growth por Continente/Região
(Revenue_t − Revenue_t-1) / Revenue_t-1 × 100

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
df["Revenue"] = df["Sales_Price"]

region_annual = (
    df.groupby(["Year", "Region"])["Revenue"]
    .sum()
    .reset_index()
    .sort_values(["Region", "Year"])
)

pivot_rev = (
    region_annual.pivot(index="Year", columns="Region", values="Revenue")
    .fillna(0)
)

pivot_yoy = pivot_rev.pct_change() * 100  # NaN no primeiro ano

col_order  = pivot_rev.sum().sort_values(ascending=False).index.tolist()
pivot_yoy  = pivot_yoy[col_order].dropna()   # remove 1.º ano
years      = pivot_yoy.index.tolist()
regions    = pivot_yoy.columns.tolist()

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
    s = pivot_yoy[r]
    stats[r] = {
        "media":      s.mean(),
        "mediana":    s.median(),
        "std":        s.std(),
        "melhor_val": s.max(),
        "melhor_ano": years[s.argmax()],
        "pior_val":   s.min(),
        "pior_ano":   years[s.argmin()],
        "pos":        (s > 0).sum(),
        "neg":        (s < 0).sum(),
        "n":          len(s),
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
    "YoY Revenue Growth por Região — Barras Agrupadas (2021–2025)",
    fontsize=13, fontweight="bold",
)

ax.axhline(0, color="#555555", linewidth=0.8, linestyle="--")

for i, r in enumerate(regions):
    vals = pivot_yoy[r].values
    bar_colors = [COLORS[r] if v >= 0 else "#d62728" for v in vals]
    bars = ax.bar(
        x + offsets[i], vals,
        width=width, color=bar_colors, alpha=0.82,
        label=LABELS[r],
    )
    for bar, val in zip(bars, vals):
        offset = 0.25 if val >= 0 else -0.25
        va = "bottom" if val >= 0 else "top"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + offset,
            f"{val:+.1f}%",
            ha="center", va=va, fontsize=7.5, fontweight="bold",
            color=COLORS[r],
        )

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:+.1f}%"))
ax.set_xticks(x)
ax.set_xticklabels(years, fontsize=11)
ax.set_xlabel("Ano", fontsize=11)
ax.set_ylabel("YoY Revenue Growth (%)", fontsize=11)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.18),
          ncol=3, fontsize=10, framealpha=0.85)
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.margins(y=0.20)

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "yoy_revenue_growth_continentes_bars.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

# ────────────────────────────────────────────────────────────────────────────────
# PNG 2 — Tabela de estatísticas
# ────────────────────────────────────────────────────────────────────────────────
row_labels = [
    "Cresc. Médio YoY",
    "Mediana YoY",
    "Desvio Padrão",
    "Melhor Ano",
    "Pior Ano",
    "Anos Positivos",
]
cell_data = [
    [f"{stats[r]['media']:+.1f}%"                                                   for r in regions],
    [f"{stats[r]['mediana']:+.1f}%"                                                 for r in regions],
    [f"{stats[r]['std']:.1f} pp"                                                    for r in regions],
    [f"{stats[r]['melhor_ano']} ({stats[r]['melhor_val']:+.1f}%)"                   for r in regions],
    [f"{stats[r]['pior_ano']} ({stats[r]['pior_val']:+.1f}%)"                       for r in regions],
    [f"{stats[r]['pos']} de {stats[r]['n']}"                                        for r in regions],
]

n_rows = len(row_labels)
fig_h  = 1.2 + n_rows * 0.55 + 0.6
fig, ax = plt.subplots(figsize=(12, fig_h))
ax.axis("off")
fig.suptitle("Estatísticas Acumuladas — YoY Revenue Growth por Região",
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
p = os.path.join(OUTPUT_DIR, "yoy_revenue_growth_continentes_stats.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

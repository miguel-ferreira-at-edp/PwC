"""
F09 — Ticket Médio por Continente/Região
AVG(Sales_Price)

Gera 3 ficheiros:
  ticket_medio_continentes_bars.png       → barras agrupadas por região
  ticket_medio_continentes_categoria.png  → barras agrupadas região × categoria
  ticket_medio_continentes_stats.png      → tabela de estatísticas
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
df = df.dropna(subset=["Main_Category"])

region_annual = (
    df.groupby(["Year", "Region"])["Sales_Price"]
    .mean()
    .reset_index()
    .rename(columns={"Sales_Price": "Ticket"})
)

pivot = (
    region_annual.pivot(index="Year", columns="Region", values="Ticket")
    .fillna(0)
)

col_order = pivot.mean().sort_values(ascending=False).index.tolist()
pivot     = pivot[col_order]
years     = pivot.index.tolist()
regions   = pivot.columns.tolist()

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
    s   = pivot[r]
    yoy = s.pct_change() * 100
    stats[r] = {
        "media":      s.mean(),
        "max_val":    s.max(),
        "max_ano":    years[s.argmax()],
        "min_val":    s.min(),
        "min_ano":    years[s.argmin()],
        "variacao":   s.iloc[-1] - s.iloc[0],
        "yoy_mean":   yoy.mean(),
    }

# ────────────────────────────────────────────────────────────────────────────────
# PNG 1 — Barras agrupadas por região
# ────────────────────────────────────────────────────────────────────────────────
n_regions = len(regions)
x         = np.arange(len(years))
width     = 0.22
offsets   = np.linspace(-(n_regions - 1) / 2, (n_regions - 1) / 2, n_regions) * width

fig, ax = plt.subplots(figsize=(14, 7))
fig.suptitle("Ticket Médio por Região — Evolução Anual (2020–2025)",
             fontsize=13, fontweight="bold")

for i, r in enumerate(regions):
    bars = ax.bar(
        x + offsets[i], pivot[r].values,
        width=width, color=COLORS[r], alpha=0.82,
        label=LABELS[r],
    )
    for bar, val in zip(bars, pivot[r].values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.4,
            f"€{val:.0f}",
            ha="center", va="bottom", fontsize=7.5,
            color=COLORS[r], fontweight="bold",
        )

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"€{v:.0f}"))
ax.set_xticks(x)
ax.set_xticklabels(years, fontsize=11)
ax.set_xlabel("Ano", fontsize=11)
ax.set_ylabel("Ticket Médio (€)", fontsize=11)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.18),
          ncol=3, fontsize=10, framealpha=0.85)
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.margins(y=0.12)

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "ticket_medio_continentes_bars.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

# ────────────────────────────────────────────────────────────────────────────────
# PNG 2 — Barras agrupadas por Categoria dentro de cada Região (último ano)
# ────────────────────────────────────────────────────────────────────────────────
cat_region = (
    df.groupby(["Region", "Main_Category"])["Sales_Price"]
    .mean()
    .reset_index()
    .rename(columns={"Sales_Price": "Ticket"})
)

categories = sorted(cat_region["Main_Category"].unique())
CAT_COLORS = {
    "Accessories":          "#4e9af1",
    "Clothing":             "#f4a02a",
    "Technical equipment":  "#3cba54",
}
palette = ["#9467bd", "#8c564b", "#e377c2"]
for i, c in enumerate(categories):
    if c not in CAT_COLORS:
        CAT_COLORS[c] = palette[i % len(palette)]

n_cats  = len(categories)
x2      = np.arange(len(regions))
width2  = 0.7 / n_cats
offsets2 = np.linspace(-(n_cats - 1) / 2, (n_cats - 1) / 2, n_cats) * width2

fig, ax = plt.subplots(figsize=(14, 7))
fig.suptitle("Ticket Médio por Região × Categoria — Período Total (2020–2025)",
             fontsize=13, fontweight="bold")

for i, cat in enumerate(categories):
    vals = []
    for r in regions:
        subset = cat_region[(cat_region["Region"] == r) & (cat_region["Main_Category"] == cat)]
        vals.append(subset["Ticket"].values[0] if len(subset) > 0 else 0)
    bars = ax.bar(
        x2 + offsets2[i], vals,
        width=width2, color=CAT_COLORS[cat], alpha=0.82,
        label=cat,
    )
    for bar, val in zip(bars, vals):
        if val > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.4,
                f"€{val:.0f}",
                ha="center", va="bottom", fontsize=8,
                color=CAT_COLORS[cat], fontweight="bold",
            )

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"€{v:.0f}"))
ax.set_xticks(x2)
ax.set_xticklabels([LABELS[r] for r in regions], fontsize=11)
ax.set_xlabel("Região", fontsize=11)
ax.set_ylabel("Ticket Médio (€)", fontsize=11)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.18),
          ncol=n_cats, fontsize=10, framealpha=0.85)
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.margins(y=0.12)

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "ticket_medio_continentes_categoria.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

# ────────────────────────────────────────────────────────────────────────────────
# PNG 3 — Tabela de estatísticas
# ────────────────────────────────────────────────────────────────────────────────
row_labels = [
    "Ticket Médio (período)",
    "Ticket Máximo (ano)",
    "Ticket Mínimo (ano)",
    "Variação Total (€)",
    "Cresc. Médio YoY",
]
cell_data = [
    [f"€{stats[r]['media']:.2f}"                                          for r in regions],
    [f"€{stats[r]['max_val']:.2f}  ({stats[r]['max_ano']})"               for r in regions],
    [f"€{stats[r]['min_val']:.2f}  ({stats[r]['min_ano']})"               for r in regions],
    [f"{stats[r]['variacao']:+.2f} €"                                     for r in regions],
    [f"{stats[r]['yoy_mean']:+.1f}%"                                      for r in regions],
]

n_rows = len(row_labels)
fig_h  = 1.2 + n_rows * 0.55 + 0.6
fig, ax = plt.subplots(figsize=(12, fig_h))
ax.axis("off")
fig.suptitle("Estatísticas Acumuladas — Ticket Médio por Região",
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
p = os.path.join(OUTPUT_DIR, "ticket_medio_continentes_stats.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

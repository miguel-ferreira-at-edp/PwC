"""
F09 — Ticket Médio Global
AVG(Sales_Price)

Gera 3 ficheiros:
  ticket_medio_global.png            → barras por ano (global)
  ticket_medio_global_categoria.png  → barras agrupadas por Main_Category
  ticket_medio_global_stats.png      → tabela de estatísticas
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

annual = (
    df.groupby("Year")["Sales_Price"]
    .mean()
    .reset_index()
    .rename(columns={"Sales_Price": "Ticket"})
    .sort_values("Year")
)

years   = annual["Year"].tolist()
tickets = annual["Ticket"]

# ── Estatísticas ───────────────────────────────────────────────────────────────
yoy = tickets.pct_change() * 100
stats_rows = [
    ("Ticket Médio Global",   f"€{tickets.mean():.2f}"),
    ("Ticket Máximo",         f"€{tickets.max():.2f}  ({years[tickets.argmax()]})"),
    ("Ticket Mínimo",         f"€{tickets.min():.2f}  ({years[tickets.argmin()]})"),
    ("Variação Total",        f"{tickets.iloc[-1] - tickets.iloc[0]:+.2f} €"),
    ("Cresc. Médio YoY",      f"{yoy.mean():+.1f}%"),
    ("Melhor Ano (YoY)",      f"{years[yoy.idxmax()]} ({yoy.max():+.1f}%)"),
    ("Pior Ano (YoY)",        f"{years[yoy.idxmin()]} ({yoy.min():+.1f}%)"),
]

# ────────────────────────────────────────────────────────────────────────────────
# PNG 1 — Barras anuais globais
# ────────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
fig.suptitle("Ticket Médio Global — Evolução Anual (2020–2025)",
             fontsize=14, fontweight="bold")

bars = ax.bar(
    annual["Year"], annual["Ticket"],
    color="#7b4f9e", alpha=0.75, width=0.5,
    label="Ticket Médio (barras)",
)
ax.plot(
    annual["Year"], annual["Ticket"],
    marker="o", color="#d62728", linewidth=2,
    label="Tendência (linha)",
)

for bar, val in zip(bars, annual["Ticket"]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + tickets.max() * 0.01,
        f"€{val:.2f}",
        ha="center", va="bottom", fontsize=9,
    )

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"€{x:.0f}"))
ax.set_xlabel("Ano", fontsize=12)
ax.set_ylabel("Ticket Médio (€)", fontsize=12)
ax.set_xticks(annual["Year"])
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.5)
ax.margins(y=0.12)

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "ticket_medio_global.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

# ────────────────────────────────────────────────────────────────────────────────
# PNG 2 — Barras agrupadas por Categoria
# ────────────────────────────────────────────────────────────────────────────────
cat_annual = (
    df.groupby(["Year", "Main_Category"])["Sales_Price"]
    .mean()
    .reset_index()
    .rename(columns={"Sales_Price": "Ticket"})
)

categories = sorted(cat_annual["Main_Category"].unique())
CAT_COLORS = {
    "Accessories":          "#4e9af1",
    "Clothing":             "#f4a02a",
    "Technical equipment":  "#3cba54",
}
# Fallback para categorias não mapeadas
palette = ["#9467bd", "#8c564b", "#e377c2", "#bcbd22"]
for i, c in enumerate(categories):
    if c not in CAT_COLORS:
        CAT_COLORS[c] = palette[i % len(palette)]

x       = np.arange(len(years))
n_cats  = len(categories)
width   = 0.7 / n_cats
offsets = np.linspace(-(n_cats - 1) / 2, (n_cats - 1) / 2, n_cats) * width

fig, ax = plt.subplots(figsize=(14, 7))
fig.suptitle("Ticket Médio por Categoria — Evolução Anual (2020–2025)",
             fontsize=13, fontweight="bold")

for i, cat in enumerate(categories):
    vals = [
        cat_annual.loc[(cat_annual["Year"] == yr) & (cat_annual["Main_Category"] == cat), "Ticket"].values[0]
        if len(cat_annual.loc[(cat_annual["Year"] == yr) & (cat_annual["Main_Category"] == cat)]) > 0
        else 0
        for yr in years
    ]
    bars = ax.bar(
        x + offsets[i], vals,
        width=width, color=CAT_COLORS[cat], alpha=0.82,
        label=cat,
    )
    for bar, val in zip(bars, vals):
        if val > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"€{val:.0f}",
                ha="center", va="bottom", fontsize=7.5,
                color=CAT_COLORS[cat], fontweight="bold",
            )

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"€{v:.0f}"))
ax.set_xticks(x)
ax.set_xticklabels(years, fontsize=11)
ax.set_xlabel("Ano", fontsize=11)
ax.set_ylabel("Ticket Médio (€)", fontsize=11)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.18),
          ncol=n_cats, fontsize=10, framealpha=0.85)
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.margins(y=0.12)

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "ticket_medio_global_categoria.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

# ────────────────────────────────────────────────────────────────────────────────
# PNG 3 — Tabela de estatísticas
# ────────────────────────────────────────────────────────────────────────────────
n_rows  = len(stats_rows)
fig_h   = 1.0 + n_rows * 0.52 + 0.5
fig, ax = plt.subplots(figsize=(7, fig_h))
ax.axis("off")
fig.suptitle("Estatísticas Acumuladas — Ticket Médio Global",
             fontsize=13, fontweight="bold", y=0.97)

cell_data  = [[v] for _, v in stats_rows]
row_labels = [l for l, _ in stats_rows]

tbl = ax.table(
    cellText=cell_data,
    rowLabels=row_labels,
    colLabels=["Valor"],
    cellLoc="center",
    rowLoc="left",
    loc="center",
    bbox=[0.0, 0.0, 1.0, 0.92],
    colWidths=[0.28, 0.72],
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(11)

tbl[(0, 0)].set_facecolor("#7b4f9e")
tbl[(0, 0)].set_text_props(color="white", fontweight="bold")
tbl[(0, 0)].set_edgecolor("#bbbbbb")
tbl[(0, 0)].set_height(0.13)

for i in range(n_rows):
    tbl[(i + 1, -1)].set_facecolor("#e8e8e8")
    tbl[(i + 1, -1)].set_text_props(fontweight="bold")
    tbl[(i + 1, -1)].set_edgecolor("#bbbbbb")
    tbl[(i + 1, -1)].set_height(0.11)
    cell = tbl[(i + 1, 0)]
    cell.set_facecolor("#f7f7f7" if i % 2 == 0 else "#ffffff")
    cell.set_edgecolor("#bbbbbb")
    cell.set_height(0.11)

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "ticket_medio_global_stats.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

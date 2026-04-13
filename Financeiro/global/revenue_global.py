"""
Revenue Global — evolução anual do revenue total (escala global).
Gera 2 ficheiros:
  revenue_global.png       → barras + linha de tendência
  revenue_global_stats.png → tabela de estatísticas acumuladas
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

global_revenue = (
    df.groupby("Year")["Revenue"]
    .sum()
    .reset_index()
    .sort_values("Year")
)

rev = global_revenue["Revenue"]
years = global_revenue["Year"].tolist()
n_years = len(years)

# ── Estatísticas ───────────────────────────────────────────────────────────────
v0, vn = rev.iloc[0], rev.iloc[-1]
cagr       = ((vn / v0) ** (1 / (n_years - 1)) - 1) * 100
yoy        = rev.pct_change() * 100
yoy_mean   = yoy.mean()
yoy_best_i = yoy.idxmax()
yoy_worst_i = yoy.idxmin()

stats_rows = [
    ("Revenue Total Acum.",  f"${rev.sum()/1e6:.1f}M"),
    ("Média Anual",          f"${rev.mean()/1e6:.2f}M"),
    ("CAGR",                 f"{cagr:.1f}%"),
    ("Cresc. Médio YoY",     f"{yoy_mean:.1f}%"),
    ("Melhor Ano (YoY)",     f"{years[yoy_best_i]} ({yoy.iloc[yoy_best_i]:+.1f}%)"),
    ("Pior Ano (YoY)",       f"{years[yoy_worst_i]} ({yoy.iloc[yoy_worst_i]:+.1f}%)"),
    ("Pico",                 f"${rev.max()/1e6:.1f}M  ({years[rev.argmax()]})"),
    ("Mínimo",               f"${rev.min()/1e6:.1f}M  ({years[rev.argmin()]})"),
]

# ────────────────────────────────────────────────────────────────────────────────
# PNG 1 — Barras + Linha
# ────────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
fig.suptitle("Revenue Global — Evolução Anual (2020–2025)",
             fontsize=14, fontweight="bold")

bars = ax.bar(
    global_revenue["Year"],
    global_revenue["Revenue"],
    color="#1f77b4",
    alpha=0.75,
    width=0.5,
    label="Revenue (barras)",
)

ax.plot(
    global_revenue["Year"],
    global_revenue["Revenue"],
    marker="o",
    color="#d62728",
    linewidth=2,
    label="Tendência (linha)",
)

for bar, val in zip(bars, global_revenue["Revenue"]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + rev.max() * 0.01,
        f"${val/1e6:.1f}M",
        ha="center", va="bottom", fontsize=9,
    )

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
ax.set_xlabel("Ano", fontsize=12)
ax.set_ylabel("Revenue", fontsize=12)
ax.set_xticks(global_revenue["Year"])
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.5)
ax.margins(y=0.12)

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "revenue_global.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

# ────────────────────────────────────────────────────────────────────────────────
# PNG 2 — Tabela de estatísticas
# ────────────────────────────────────────────────────────────────────────────────
n_rows  = len(stats_rows)
fig_h   = 1.0 + n_rows * 0.52 + 0.5
fig, ax = plt.subplots(figsize=(7, fig_h))
ax.axis("off")
fig.suptitle("Estatísticas Acumuladas — Revenue Global",
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

# Cabeçalho
tbl[(0, 0)].set_facecolor("#1f77b4")
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
p = os.path.join(OUTPUT_DIR, "revenue_global_stats.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

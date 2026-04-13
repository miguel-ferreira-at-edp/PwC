"""
F07 — YoY Revenue Growth Global
(Revenue_t − Revenue_t-1) / Revenue_t-1 × 100

Gera 2 ficheiros:
  yoy_revenue_growth_global.png       → barras (positivo/negativo) + linha
  yoy_revenue_growth_global_stats.png → tabela de estatísticas
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

annual = (
    df.groupby("Year")["Revenue"]
    .sum()
    .reset_index()
    .sort_values("Year")
)
annual["YoY"] = annual["Revenue"].pct_change() * 100

# Remove o primeiro ano (NaN)
annual_yoy = annual.dropna(subset=["YoY"]).copy()
years      = annual_yoy["Year"].tolist()
yoy        = annual_yoy["YoY"]

# ── Estatísticas ───────────────────────────────────────────────────────────────
stats_rows = [
    ("Cresc. Médio YoY",    f"{yoy.mean():+.1f}%"),
    ("Melhor Ano",          f"{years[yoy.argmax()]} ({yoy.max():+.1f}%)"),
    ("Pior Ano",            f"{years[yoy.argmin()]} ({yoy.min():+.1f}%)"),
    ("Anos Positivos",      f"{(yoy > 0).sum()} de {len(yoy)}"),
    ("Anos Negativos",      f"{(yoy < 0).sum()} de {len(yoy)}"),
    ("Mediana YoY",         f"{yoy.median():+.1f}%"),
    ("Desvio Padrão",       f"{yoy.std():.1f} pp"),
]

# ────────────────────────────────────────────────────────────────────────────────
# PNG 1 — Barras + Linha
# ────────────────────────────────────────────────────────────────────────────────
colors_bar = ["#2ca02c" if v >= 0 else "#d62728" for v in yoy]

fig, ax = plt.subplots(figsize=(12, 6))
fig.suptitle("YoY Revenue Growth Global — Evolução Anual (2021–2025)",
             fontsize=14, fontweight="bold")

bars = ax.bar(
    annual_yoy["Year"],
    annual_yoy["YoY"],
    color=colors_bar,
    alpha=0.75,
    width=0.5,
    label="YoY Growth (barras)",
)

ax.plot(
    annual_yoy["Year"],
    annual_yoy["YoY"],
    marker="o",
    color="#1f77b4",
    linewidth=2,
    label="Tendência (linha)",
)

ax.axhline(0, color="#555555", linewidth=0.8, linestyle="--")

for bar, val in zip(bars, annual_yoy["YoY"]):
    offset = abs(yoy.max() - yoy.min()) * 0.02
    va     = "bottom" if val >= 0 else "top"
    y_pos  = val + offset if val >= 0 else val - offset
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        y_pos,
        f"{val:+.1f}%",
        ha="center", va=va, fontsize=9,
    )

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:+.1f}%"))
ax.set_xlabel("Ano", fontsize=12)
ax.set_ylabel("YoY Revenue Growth (%)", fontsize=12)
ax.set_xticks(annual_yoy["Year"])
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.5)
ax.margins(y=0.15)

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "yoy_revenue_growth_global.png")
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
fig.suptitle("Estatísticas Acumuladas — YoY Revenue Growth Global",
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
p = os.path.join(OUTPUT_DIR, "yoy_revenue_growth_global_stats.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

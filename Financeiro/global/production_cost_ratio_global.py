"""
F06 — Production Cost Ratio Global
SUM(Production_Cost) / SUM(Sales_Price) × 100

Gera 2 ficheiros:
  production_cost_ratio_global.png       → barras + linha de tendência
  production_cost_ratio_global_stats.png → tabela de estatísticas acumuladas
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

annual = (
    df.groupby("Year")
    .agg(Production_Cost=("Production_Cost", "sum"),
         Sales_Price=("Sales_Price", "sum"))
    .reset_index()
    .sort_values("Year")
)
annual["PCR"] = annual["Production_Cost"] / annual["Sales_Price"] * 100

years   = annual["Year"].tolist()
pcr     = annual["PCR"]
n_years = len(years)

# ── Estatísticas ───────────────────────────────────────────────────────────────
yoy      = pcr.diff()          # variação absoluta pp ano a ano
stats_rows = [
    ("PCR Médio (período)",   f"{pcr.mean():.1f}%"),
    ("PCR Mínimo",            f"{pcr.min():.1f}%  ({years[pcr.argmin()]})"),
    ("PCR Máximo",            f"{pcr.max():.1f}%  ({years[pcr.argmax()]})"),
    ("Variação Total (pp)",   f"{pcr.iloc[-1] - pcr.iloc[0]:+.1f} pp"),
    ("Var. Média YoY (pp)",   f"{yoy.mean():+.1f} pp"),
    ("Melhor Ano (↓ custo)",  f"{years[yoy.idxmin()]} ({yoy.min():+.1f} pp)"),
    ("Pior Ano (↑ custo)",    f"{years[yoy.idxmax()]} ({yoy.max():+.1f} pp)"),
]

# ────────────────────────────────────────────────────────────────────────────────
# PNG 1 — Barras + Linha
# ────────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
fig.suptitle("Production Cost Ratio Global — Evolução Anual (2020–2025)",
             fontsize=14, fontweight="bold")

bars = ax.bar(
    annual["Year"],
    annual["PCR"],
    color="#e07b39",
    alpha=0.75,
    width=0.5,
    label="PCR (barras)",
)

ax.plot(
    annual["Year"],
    annual["PCR"],
    marker="o",
    color="#d62728",
    linewidth=2,
    label="Tendência (linha)",
)

for bar, val in zip(bars, annual["PCR"]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + pcr.max() * 0.01,
        f"{val:.1f}%",
        ha="center", va="bottom", fontsize=9,
    )

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}%"))
ax.set_xlabel("Ano", fontsize=12)
ax.set_ylabel("Production Cost Ratio (%)", fontsize=12)
ax.set_xticks(annual["Year"])
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.5)
ax.margins(y=0.12)

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "production_cost_ratio_global.png")
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
fig.suptitle("Estatísticas Acumuladas — Production Cost Ratio Global",
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

tbl[(0, 0)].set_facecolor("#e07b39")
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
p = os.path.join(OUTPUT_DIR, "production_cost_ratio_global_stats.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

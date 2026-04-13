"""
Gross Margin Global — evolução anual da margem bruta (escala global).
Fórmula: (Sales_Price - Production_Cost) / Sales_Price * 100
Gera 2 ficheiros:
  gross_margin_global.png       → barras + linha de tendência
  gross_margin_global_stats.png → tabela de estatísticas acumuladas
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
# Gross Margin = (Gross Profit / Revenue) * 100
df["Gross_Profit"] = df["Sales_Price"] - df["Production_Cost"]
df["Revenue"] = df["Sales_Price"]

global_data = df.groupby("Year").agg({
    "Gross_Profit": "sum",
    "Revenue": "sum"
}).reset_index()

global_data["Gross_Margin"] = (global_data["Gross_Profit"] / global_data["Revenue"]) * 100
global_data = global_data.sort_values("Year")

val_col = global_data["Gross_Margin"]
years = global_data["Year"].tolist()
n_years = len(years)

# ── Estatísticas ───────────────────────────────────────────────────────────────
v0, vn = val_col.iloc[0], val_col.iloc[-1]
cagr       = ((vn / v0) ** (1 / (n_years - 1)) - 1) * 100
yoy        = val_col.pct_change() * 100

stats_data = [
    ["Margem Bruta Média",         f"{val_col.mean():.1f}%"],
    ["CAGR da Margem",              f"{cagr:.1f}%"],
    ["Cresc. Médio YoY",           f"{yoy.mean():.1f}%"],
    ["Melhor Ano (Margem)",        f"{years[val_col.idxmax()]} ({val_col.max():.1f}%)"],
    ["Pior Ano (Margem)",          f"{years[val_col.idxmin()]} ({val_col.min():.1f}%)"],
    ["Pico (Margem)",              f"{val_col.max():.1f}% ({years[val_col.argmax()]})"],
    ["Mínimo (Margem)",            f"{val_col.min():.1f}% ({years[val_col.argmin()]})"],
]

# ────────────────────────────────────────────────────────────────────────────────
# PNG 1 — Barras + Linha
# ────────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
fig.suptitle("Gross Margin Global — Evolução Anual (%)",
             fontsize=14, fontweight="bold")

bars = ax.bar(
    global_data["Year"],
    global_data["Gross_Margin"],
    color="#1a7a32",
    alpha=0.75,
    width=0.5,
    label="Gross Margin % (barras)",
)

ax.plot(
    global_data["Year"],
    global_data["Gross_Margin"],
    marker="o",
    color="#d62728",
    linewidth=2,
    label="Tendência (linha)",
)

for bar, val in zip(bars, global_data["Gross_Margin"]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + val_col.max() * 0.01,
        f"{val:.1f}%",
        ha="center", va="bottom", fontsize=9,
    )

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
ax.set_xlabel("Ano", fontsize=12)
ax.set_ylabel("Gross Margin (%)", fontsize=12)
ax.set_xticks(global_data["Year"])
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.5)
ax.margins(y=0.12)

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "gross_margin_global.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
plt.close()

# ────────────────────────────────────────────────────────────────────────────────
# PNG 2 — Tabela de estatísticas
# ────────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
ax.axis("off")
fig.suptitle("Estatísticas Acumuladas — Gross Margin Global",
             fontsize=13, fontweight="bold", y=0.95)

tbl = ax.table(
    cellText=stats_data,
    colLabels=["Indicador", "Valor"],
    cellLoc="center",
    loc="center",
    colWidths=[0.48, 0.42]
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(11)

for (i, j), cell in tbl.get_celld().items():
    cell.set_height(0.12)
    if i == 0:
        cell.set_facecolor("#1a7a32")
        cell.set_text_props(color="white", fontweight="bold")
    elif j == 0:
        cell.set_facecolor("#f0f0f0")
        cell.set_text_props(fontweight="bold", ha="left")
    else:
        cell.set_facecolor("white")

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "gross_margin_global_stats.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
plt.close()

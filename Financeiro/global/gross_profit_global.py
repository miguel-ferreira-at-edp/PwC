"""
Gross Profit Global — evolução anual do gross profit total (escala global).
Gera 2 ficheiros:
  gross_profit_global.png       → barras + linha de tendência
  gross_profit_global_stats.png → tabela de estatísticas acumuladas
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
# Gross Profit = Sales_Price - Production_Cost
df["Gross_Profit"] = df["Sales_Price"] - df["Production_Cost"]

global_gp = (
    df.groupby("Year")["Gross_Profit"]
    .sum()
    .reset_index()
    .sort_values("Year")
)

val_col = global_gp["Gross_Profit"]
years = global_gp["Year"].tolist()
n_years = len(years)

# ── Estatísticas ───────────────────────────────────────────────────────────────
v0, vn = val_col.iloc[0], val_col.iloc[-1]
cagr       = ((vn / v0) ** (1 / (n_years - 1)) - 1) * 100
yoy        = val_col.pct_change() * 100
yoy_mean   = yoy.mean()
yoy_best_i = yoy.idxmax()
yoy_worst_i = yoy.idxmin()

# Mudança de estrutura: [Indicador, Valor] em vez de usar rowLabels
stats_data = [
    ["Gross Profit Total Acum.",  f"${val_col.sum()/1e6:.1f}M"],
    ["Média Anual",               f"${val_col.mean()/1e6:.2f}M"],
    ["CAGR",                      f"{cagr:.1f}%"],
    ["Cresc. Médio YoY",          f"{yoy_mean:.1f}%"],
    ["Melhor Ano (YoY)",          f"{years[yoy_best_i]} ({yoy.iloc[yoy_best_i]:+.1f}%)"],
    ["Pior Ano (YoY)",            f"{years[yoy_worst_i]} ({yoy.iloc[yoy_worst_i]:+.1f}%)"],
    ["Pico",                      f"${val_col.max()/1e6:.1f}M  ({years[val_col.argmax()]})"],
    ["Mínimo",                    f"${val_col.min()/1e6:.1f}M  ({years[val_col.argmin()]})"],
]

# ────────────────────────────────────────────────────────────────────────────────
# PNG 1 — Barras + Linha
# ────────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
fig.suptitle("Gross Profit Global — Evolução Anual (2020–2025)",
             fontsize=14, fontweight="bold")

bars = ax.bar(
    global_gp["Year"],
    global_gp["Gross_Profit"],
    color="#2ca02c",
    alpha=0.75,
    width=0.5,
    label="Gross Profit (barras)",
)

ax.plot(
    global_gp["Year"],
    global_gp["Gross_Profit"],
    marker="o",
    color="#d62728",
    linewidth=2,
    label="Tendência (linha)",
)

for bar, val in zip(bars, global_gp["Gross_Profit"]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + val_col.max() * 0.01,
        f"${val/1e6:.1f}M",
        ha="center", va="bottom", fontsize=9,
    )

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
ax.set_xlabel("Ano", fontsize=12)
ax.set_ylabel("Gross Profit", fontsize=12)
ax.set_xticks(global_gp["Year"])
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.5)
ax.margins(y=0.12)

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "gross_profit_global.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

# ────────────────────────────────────────────────────────────────────────────────
# PNG 2 — Tabela de estatísticas (Nova estrutura robusta)
# ────────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
ax.axis("off")
fig.suptitle("Estatísticas Acumuladas — Gross Profit Global",
             fontsize=13, fontweight="bold", y=0.95)

tbl = ax.table(
    cellText=stats_data,
    colLabels=["Indicador", "Valor"],
    cellLoc="center",
    loc="center",
    colWidths=[0.48, 0.42] # Larguras explícitas
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(11)

# Estilização das células
for (i, j), cell in tbl.get_celld().items():
    cell.set_height(0.12)
    if i == 0: # Cabeçalho
        cell.set_facecolor("#2ca02c")
        cell.set_text_props(color="white", fontweight="bold")
    elif j == 0: # Coluna de indicadores
        cell.set_facecolor("#f0f0f0")
        cell.set_text_props(fontweight="bold", ha="left")
    else: # Coluna de valores
        cell.set_facecolor("white")

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, "gross_profit_global_stats.png")
plt.savefig(p, dpi=150, bbox_inches="tight")
print(f"Guardado: {p}")
plt.close()

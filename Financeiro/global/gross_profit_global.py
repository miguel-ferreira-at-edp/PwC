"""
Gross Profit Global — evolução anual do Gross Profit total (escala global).
Gráfico combinado: barras + linha de tendência.
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

# ── Plot ───────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))

# Barras
bars = ax.bar(
    global_gp["Year"],
    global_gp["Gross_Profit"],
    color="#2ca02c",  # Verde para Profit
    alpha=0.75,
    width=0.5,
    label="Gross Profit (barras)",
)

# Linha de tendência
ax.plot(
    global_gp["Year"],
    global_gp["Gross_Profit"],
    marker="o",
    color="#d62728",
    linewidth=2,
    label="Tendência (linha)",
)

# Anotações nos topo das barras
for bar, val in zip(bars, global_gp["Gross_Profit"]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + global_gp["Gross_Profit"].max() * 0.01,
        f"${val/1e6:.1f}M",
        ha="center",
        va="bottom",
        fontsize=9,
    )

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
ax.set_xlabel("Ano", fontsize=12)
ax.set_ylabel("Gross Profit", fontsize=12)
ax.set_title("Gross Profit Global — Evolução Anual", fontsize=14, fontweight="bold")
ax.set_xticks(global_gp["Year"])
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()

out_path = os.path.join(OUTPUT_DIR, "gross_profit_global.png")
plt.savefig(out_path, dpi=150)
print(f"Gráfico guardado em: {out_path}")
# plt.show()

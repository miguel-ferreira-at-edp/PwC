"""
Revenue Global — evolução anual do revenue total (escala global).
Gráfico combinado: barras + linha de tendência.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "..", "..", "data", "sales_data_clean.csv")
OUTPUT_DIR = BASE_DIR  # gráficos guardados na mesma pasta

# ── Load & prepare ─────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
df["Revenue"] = df["Sales_Price"] - df["Production_Cost"] - df["Shipping_Cost"]

global_revenue = (
    df.groupby("Year")["Revenue"]
    .sum()
    .reset_index()
    .sort_values("Year")
)

# ── Plot ───────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))

# Barras
bars = ax.bar(
    global_revenue["Year"],
    global_revenue["Revenue"],
    color="#1f77b4",
    alpha=0.75,
    width=0.5,
    label="Revenue (barras)",
)

# Linha de tendência
ax.plot(
    global_revenue["Year"],
    global_revenue["Revenue"],
    marker="o",
    color="#d62728",
    linewidth=2,
    label="Tendência (linha)",
)

# Anotações nos topo das barras
for bar, val in zip(bars, global_revenue["Revenue"]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + global_revenue["Revenue"].max() * 0.01,
        f"${val/1e6:.1f}M",
        ha="center",
        va="bottom",
        fontsize=9,
    )

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
ax.set_xlabel("Ano", fontsize=12)
ax.set_ylabel("Revenue", fontsize=12)
ax.set_title("Revenue Global — Evolução Anual", fontsize=14, fontweight="bold")
ax.set_xticks(global_revenue["Year"])
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()

out_path = os.path.join(OUTPUT_DIR, "revenue_global.png")
plt.savefig(out_path, dpi=150)
print(f"Gráfico guardado em: {out_path}")
plt.show()

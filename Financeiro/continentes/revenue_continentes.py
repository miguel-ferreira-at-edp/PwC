"""
Revenue por Continente/Região — evolução anual por Europa, Ásia e América do Norte.
Gráfico combinado: barras agrupadas por região + linhas de tendência por região.
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
df["Revenue"] = df["Sales_Price"] - df["Production_Cost"] - df["Shipping_Cost"]

region_revenue = (
    df.groupby(["Year", "Region"])["Revenue"]
    .sum()
    .reset_index()
    .sort_values(["Year", "Region"])
)

# Pivot para facilitar plot
pivot = region_revenue.pivot(index="Year", columns="Region", values="Revenue").fillna(0)
years  = pivot.index.tolist()
regions = pivot.columns.tolist()

COLORS = {
    "Asia":          "#1f77b4",
    "Europe":        "#ff7f0e",
    "North America": "#2ca02c",
}

# ── Plot ───────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(12, 12), sharex=True)
fig.suptitle("Revenue por Região — Evolução Anual", fontsize=15, fontweight="bold", y=0.98)

# ── Subplot 1: Barras agrupadas ────────────────────────────────────────────────
ax1 = axes[0]
n_regions  = len(regions)
bar_width  = 0.25
x          = range(len(years))

for i, region in enumerate(regions):
    offset = (i - n_regions / 2 + 0.5) * bar_width
    bars   = ax1.bar(
        [xi + offset for xi in x],
        pivot[region],
        width=bar_width,
        label=region,
        color=COLORS.get(region, f"C{i}"),
        alpha=0.8,
    )

ax1.set_ylabel("Revenue", fontsize=11)
ax1.set_title("Barras Agrupadas por Região", fontsize=12)
ax1.set_xticks(list(x))
ax1.set_xticklabels(years)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e6:.1f}M"))
ax1.legend(title="Região")
ax1.grid(axis="y", linestyle="--", alpha=0.4)

# ── Subplot 2: Linhas por região ───────────────────────────────────────────────
ax2 = axes[1]

for region in regions:
    ax2.plot(
        years,
        pivot[region],
        marker="o",
        linewidth=2,
        label=region,
        color=COLORS.get(region, None),
    )
    # Anotações no último ponto
    last_val = pivot[region].iloc[-1]
    ax2.annotate(
        f"${last_val/1e6:.1f}M",
        xy=(years[-1], last_val),
        xytext=(5, 0),
        textcoords="offset points",
        fontsize=8,
        color=COLORS.get(region, "black"),
    )

ax2.set_xlabel("Ano", fontsize=11)
ax2.set_ylabel("Revenue", fontsize=11)
ax2.set_title("Linha de Tendência por Região", fontsize=12)
ax2.set_xticks(years)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e6:.1f}M"))
ax2.legend(title="Região")
ax2.grid(linestyle="--", alpha=0.4)

plt.tight_layout()
out_path = os.path.join(OUTPUT_DIR, "revenue_continentes.png")
plt.savefig(out_path, dpi=150)
print(f"Gráfico guardado em: {out_path}")
plt.show()

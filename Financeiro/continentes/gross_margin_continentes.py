"""
Gross Margin por Continente/Região — evolução anual.
Fórmula: (Gross Profit / Revenue) * 100
Gera 2 ficheiros separados:
  gross_margin_continentes.png       → linhas por região
  gross_margin_continentes_stats.png → tabela de estatísticas acumuladas
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
df["Gross_Profit"] = df["Sales_Price"] - df["Production_Cost"]
df["Revenue"] = df["Sales_Price"]

region_data = df.groupby(["Year", "Region"]).agg({
    "Gross_Profit": "sum",
    "Revenue": "sum"
}).reset_index()

region_data["Gross_Margin"] = (region_data["Gross_Profit"] / region_data["Revenue"]) * 100

pivot = region_data.pivot(index="Year", columns="Region", values="Gross_Margin").fillna(0)
years = pivot.index.tolist()
regions = pivot.columns.tolist()
n_years = len(years)

COLORS = {"Asia": "#4e9af1", "Europe": "#f4a02a", "North America": "#3cba54"}
LABELS = {"Asia": "Ásia", "Europe": "Europa", "North America": "América do Norte"}

def cagr(series):
    v0, vn = series.iloc[0], series.iloc[-1]
    if v0 <= 0: return float("nan")
    return ((vn / v0) ** (1 / (n_years - 1)) - 1) * 100

# ── Estatísticas ───────────────────────────────────────────────────────────────
stats = {}
for r in regions:
    s = pivot[r]
    stats[r] = {
        "media": s.mean(),
        "cagr": cagr(s),
        "yoy_mean": s.pct_change().mean() * 100,
        "pico_ano": years[s.argmax()],
        "pico_val": s.max(),
        "min_ano": years[s.argmin()],
        "min_val": s.min(),
    }

# ────────────────────────────────────────────────────────────────────────────────
# PNG 1 — Gráfico de Linhas por Região
# ────────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
fig.suptitle("Gross Margin por Região — Evolução Anual (%)", fontsize=14, fontweight="bold")

for region in regions:
    ax.plot(years, pivot[region], marker="o", linewidth=2.5, label=LABELS.get(region, region), color=COLORS.get(region))
    
    # Anotação no último valor
    final_val = pivot[region].iloc[-1]
    ax.text(years[-1] + 0.05, final_val, f"{final_val:.1f}%", color=COLORS.get(region), fontweight="bold", va="center")

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.set_xlabel("Ano", fontsize=11)
ax.set_ylabel("Gross Margin (%)", fontsize=11)
ax.legend(title="Região", loc="upper left")
ax.grid(linestyle="--", alpha=0.4)
ax.set_xlim(years[0]-0.2, years[-1]+0.8)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "gross_margin_continentes.png"), dpi=150)
plt.close()

# ────────────────────────────────────────────────────────────────────────────────
# PNG 2 — Tabela de estatísticas
# ────────────────────────────────────────────────────────────────────────────────
row_labels = ["Média de Margem", "CAGR da Margem", "Cresc. Médio YoY", "Pico (ano)", "Mínimo (ano)"]
cell_data = [
    [f"{stats[r]['media']:.1f}%" for r in regions],
    [f"{stats[r]['cagr']:.1f}%" for r in regions],
    [f"{stats[r]['yoy_mean']:.1f}%" for r in regions],
    [f"{stats[r]['pico_val']:.1f}% ({stats[r]['pico_ano']})" for r in regions],
    [f"{stats[r]['min_val']:.1f}% ({stats[r]['min_ano']})" for r in regions],
]

fig_h = 1.2 + len(row_labels) * 0.55 + 0.6
fig, ax = plt.subplots(figsize=(10, fig_h))
ax.axis("off")
fig.suptitle("Estatísticas — Gross Margin por Região", fontsize=13, fontweight="bold", y=0.97)

tbl = ax.table(
    cellText=cell_data,
    rowLabels=row_labels,
    colLabels=[LABELS[r] for r in regions],
    cellLoc="center", loc="center", bbox=[0.0, 0.0, 1.0, 0.92],
    colWidths=[0.28] + [0.72 / len(regions)] * len(regions)
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(10.5)

for j, r in enumerate(regions):
    cell = tbl[(0, j)]; cell.set_facecolor(COLORS[r]); cell.set_text_props(color="white", fontweight="bold")
for i in range(len(row_labels)):
    tbl[(i+1, -1)].set_facecolor("#e8e8e8"); tbl[(i+1, -1)].set_text_props(fontweight="bold")

plt.savefig(os.path.join(OUTPUT_DIR, "gross_margin_continentes_stats.png"), dpi=150, bbox_inches="tight")
plt.close()

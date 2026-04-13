"""
Revenue por Continente/Região — evolução anual.
  - Stacked Area: volume absoluto + 100% stacked
  - Anotações dentro das bandas ano a ano (sem sobreposição)
  - Tabela de estatísticas num subplot dedicado e bem dimensionado
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

region_revenue = (
    df.groupby(["Year", "Region"])["Revenue"]
    .sum()
    .reset_index()
    .sort_values(["Year", "Region"])
)

pivot = (
    region_revenue
    .pivot(index="Year", columns="Region", values="Revenue")
    .fillna(0)
)

col_order = pivot.sum().sort_values(ascending=False).index.tolist()
pivot     = pivot[col_order]
years     = pivot.index.tolist()
regions   = pivot.columns.tolist()
n_years   = len(years)

COLORS = {
    "Asia":          "#4e9af1",
    "Europe":        "#f4a02a",
    "North America": "#3cba54",
}
LABELS = {
    "Asia":          "Ásia",
    "Europe":        "Europa",
    "North America": "América do Norte",
}

def cagr(series):
    v0, vn = series.iloc[0], series.iloc[-1]
    if v0 <= 0:
        return float("nan")
    return ((vn / v0) ** (1 / (n_years - 1)) - 1) * 100

# ── Estatísticas ───────────────────────────────────────────────────────────────
stats = {}
for r in regions:
    s = pivot[r]
    stats[r] = {
        "total":    s.sum(),
        "media":    s.mean(),
        "cagr":     cagr(s),
        "yoy_mean": s.pct_change().mean() * 100,
        "pico_ano": years[s.argmax()],
        "pico_val": s.max(),
        "min_ano":  years[s.argmin()],
        "min_val":  s.min(),
    }

# ── Layout: 3 linhas — gráfico absoluto | gráfico % | tabela ──────────────────
fig = plt.figure(figsize=(16, 17))
fig.suptitle("Revenue por Região — Evolução Anual (2020–2025)",
             fontsize=15, fontweight="bold", y=0.995)

gs = fig.add_gridspec(
    3, 1,
    height_ratios=[4.5, 4.5, 3.0],
    hspace=0.55,
    top=0.96, bottom=0.03, left=0.07, right=0.97,
)
ax1      = fig.add_subplot(gs[0])
ax2      = fig.add_subplot(gs[1])
ax_table = fig.add_subplot(gs[2])
ax_table.axis("off")

vals   = [pivot[r].values for r in regions]
colors = [COLORS[r] for r in regions]
labels = [LABELS[r] for r in regions]

# ── helpers ────────────────────────────────────────────────────────────────────
total_per_year = pivot[regions].sum(axis=1)
cumsum         = pivot[regions].cumsum(axis=1)
pivot_pct      = pivot[regions].div(total_per_year, axis=0) * 100
cumsum_pct     = pivot_pct.cumsum(axis=1)

MIN_BAND_FRAC = 0.13   # só anota valor se a banda ocupa >13% do total

# ── Subplot 1: Volume absoluto ─────────────────────────────────────────────────
ax1.stackplot(years, vals, labels=labels, colors=colors, alpha=0.85)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e6:.1f}M"))
ax1.set_xlim(years[0], years[-1])
ax1.set_xticks(years)
ax1.tick_params(axis="x", labelsize=10)
ax1.set_ylabel("Revenue", fontsize=11)
ax1.set_title("Volume Absoluto — Contribuição por Região", fontsize=12, pad=8)
ax1.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22),
           ncol=3, fontsize=9, framealpha=0.85)
ax1.grid(axis="y", linestyle="--", alpha=0.35)
ax1.margins(y=0.12)   # espaço acima do topo para os totais

# Total do stack: acima da área, rotacionado 45° para não colidir
for yr, tot in zip(years, total_per_year):
    ax1.text(
        yr, tot * 1.025,
        f"${tot/1e6:.1f}M",
        ha="center", va="bottom", fontsize=8,
        color="#111111", fontweight="bold", rotation=0,
    )

# Valor dentro de cada banda
for region in regions:
    for yr, tot_yr in zip(years, total_per_year):
        val   = pivot[region].loc[yr]
        y_mid = cumsum[region].loc[yr] - val / 2
        if val / tot_yr > MIN_BAND_FRAC:
            ax1.text(
                yr, y_mid,
                f"${val/1e6:.1f}M",
                ha="center", va="center",
                fontsize=7.5, color="black", fontweight="bold",
            )

# ── Subplot 2: 100% Stacked ────────────────────────────────────────────────────
vals_pct = [pivot_pct[r].values for r in regions]

ax2.stackplot(years, vals_pct, labels=labels, colors=colors, alpha=0.85)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax2.set_xlim(years[0], years[-1])
ax2.set_xticks(years)
ax2.tick_params(axis="x", labelsize=10)
ax2.set_ylim(0, 110)
ax2.set_xlabel("Ano", fontsize=11)
ax2.set_ylabel("Quota de Revenue (%)", fontsize=11)
ax2.set_title("Quota Relativa por Região — 100% Stacked", fontsize=12, pad=8)
ax2.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22),
           ncol=3, fontsize=9, framealpha=0.85)
ax2.grid(axis="y", linestyle="--", alpha=0.35)

for region in regions:
    for yr in years:
        pct   = pivot_pct[region].loc[yr]
        y_mid = cumsum_pct[region].loc[yr] - pct / 2
        if pct > 10:
            ax2.text(
                yr, y_mid,
                f"{pct:.1f}%",
                ha="center", va="center",
                fontsize=8, color="black", fontweight="bold",
            )

# ── Tabela de estatísticas via matplotlib.table ────────────────────────────────
row_labels = [
    "Revenue Total Acum.",
    "Média Anual",
    "CAGR",
    "Cresc. Médio YoY",
    "Pico (ano)",
    "Mínimo (ano)",
]
col_labels = [LABELS[r] for r in regions]

cell_data = [
    [f"${stats[r]['total']/1e6:.1f}M"                                    for r in regions],
    [f"${stats[r]['media']/1e6:.2f}M"                                    for r in regions],
    [f"{stats[r]['cagr']:.1f}%"                                          for r in regions],
    [f"{stats[r]['yoy_mean']:.1f}%"                                      for r in regions],
    [f"${stats[r]['pico_val']/1e6:.1f}M  ({stats[r]['pico_ano']})"       for r in regions],
    [f"${stats[r]['min_val']/1e6:.1f}M  ({stats[r]['min_ano']})"         for r in regions],
]

tbl = ax_table.table(
    cellText=cell_data,
    rowLabels=row_labels,
    colLabels=col_labels,
    cellLoc="center",
    rowLoc="left",
    loc="center",
    bbox=[0.0, 0.0, 1.0, 1.0],   # preenche o subplot por inteiro
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(9.5)

# Estilo do cabeçalho de colunas
for j, region in enumerate(regions):
    cell = tbl[(0, j)]
    cell.set_facecolor(COLORS[region])
    cell.set_text_props(color="white", fontweight="bold")
    cell.set_edgecolor("#cccccc")

# Estilo do cabeçalho de linhas + células
for i in range(len(row_labels)):
    # row header
    tbl[(i + 1, -1)].set_facecolor("#f0f0f0")
    tbl[(i + 1, -1)].set_text_props(fontweight="bold")
    tbl[(i + 1, -1)].set_edgecolor("#cccccc")
    for j in range(len(regions)):
        cell = tbl[(i + 1, j)]
        cell.set_facecolor("#fafafa" if i % 2 == 0 else "#ffffff")
        cell.set_edgecolor("#cccccc")

ax_table.set_title("Estatísticas Acumuladas por Região", fontsize=11,
                   fontweight="bold", pad=6)

out_path = os.path.join(OUTPUT_DIR, "revenue_continentes.png")
plt.savefig(out_path, dpi=150, bbox_inches="tight")
print(f"Gráfico guardado em: {out_path}")
plt.show()

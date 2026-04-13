"""
Gross Margin por País — 3 regiões × 2 ficheiros cada:
  _abs.png   → Gráfico de linhas evolução da margem
  _stats.png → Tabela de estatísticas acumuladas
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

country_data = df.groupby(["Year", "Region", "Country"]).agg({
    "Gross_Profit": "sum",
    "Revenue": "sum"
}).reset_index()

country_data["Gross_Margin"] = (country_data["Gross_Profit"] / country_data["Revenue"]) * 100

REGION_CONFIG = {
    "Asia": {"label": "Ásia", "countries": ["China", "Japan", "South Korea"], "colors": ["#1a6faf", "#4e9af1", "#a8d1f5"]},
    "Europe": {"label": "Europa", "countries": ["Andorra", "Austria", "France", "Italy", "Spain", "Switzerland"], "colors": ["#b35c00", "#f4a02a", "#ffd080", "#d62728", "#9467bd", "#e377c2"]},
    "North America": {"label": "América do Norte", "countries": ["Canada", "USA"], "colors": ["#1a7a32", "#3cba54"]},
}

def cagr(series):
    v0, vn = series.iloc[0], series.iloc[-1]
    if v0 <= 0: return float("nan")
    return ((vn / v0) ** (1 / (len(series) - 1)) - 1) * 100

def plot_region(region_key, config):
    label, countries, colors = config["label"], config["countries"], config["colors"]
    data = country_data[country_data["Region"] == region_key]
    years = sorted(data["Year"].unique())
    pivot = data.pivot_table(index="Year", columns="Country", values="Gross_Margin", aggfunc="sum").reindex(columns=countries).fillna(0)

    # ────────────────────────────────────────────────────────────────────────────
    # PNG 1 — Linhas por País
    # ────────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle(f"Gross Margin por País — {label} (%)", fontsize=14, fontweight="bold")

    for country, color in zip(countries, colors):
        if country in pivot.columns:
            ax.plot(years, pivot[country], marker="o", linewidth=2, label=country, color=color)
            final_val = pivot[country].iloc[-1]
            ax.text(years[-1]+0.05, final_val, f"{final_val:.1f}%", color=color, fontweight="bold", fontsize=9, va="center")

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_xticks(years)
    ax.set_xlabel("Ano", fontsize=11); ax.set_ylabel("Gross Margin (%)", fontsize=11)
    ax.legend(title="País", loc="upper left", fontsize=9)
    ax.grid(linestyle="--", alpha=0.35); ax.set_xlim(years[0]-0.2, years[-1]+0.8)

    p = os.path.join(OUTPUT_DIR, f"gross_margin_paises_{region_key.lower().replace(' ', '_')}.png")
    plt.savefig(p, dpi=150, bbox_inches="tight"); plt.close()

    # ────────────────────────────────────────────────────────────────────────────
    # PNG 2 — Estatísticas
    # ────────────────────────────────────────────────────────────────────────────
    row_labels = ["Média Bruta", "CAGR", "Cresc. YoY", "Pico (%)", "Mínimo (%)"]
    cell_data = []
    for rl in row_labels:
        row = []
        for c in countries:
            s = pivot[c]
            if rl == "Média Bruta": row.append(f"{s.mean():.1f}%")
            elif rl == "CAGR": row.append(f"{cagr(s):.1f}%")
            elif rl == "Cresc. YoY": row.append(f"{s.pct_change().mean()*100:.1f}%")
            elif rl == "Pico (%)": row.append(f"{s.max():.1f}% ({years[s.argmax()]})")
            elif rl == "Mínimo (%)": row.append(f"{s.min():.1f}% ({years[s.argmin()]})")
        cell_data.append(row)

    fig, ax = plt.subplots(figsize=(max(8, 2.5 * len(countries)), 4))
    ax.axis("off"); fig.suptitle(f"Estatísticas — Gross Margin {label}", fontsize=12, fontweight="bold")
    tbl = ax.table(cellText=cell_data, rowLabels=row_labels, colLabels=countries, cellLoc="center", loc="center", bbox=[0, 0, 1, 0.9])
    tbl.auto_set_font_size(False); tbl.set_fontsize(9)
    for j, c in enumerate(countries):
        cell = tbl[(0, j)]; cell.set_facecolor(colors[j]); cell.set_text_props(color="white", fontweight="bold")
    
    p = os.path.join(OUTPUT_DIR, f"gross_margin_paises_{region_key.lower().replace(' ', '_')}_stats.png")
    plt.savefig(p, dpi=150, bbox_inches="tight"); plt.close()

for rk, conf in REGION_CONFIG.items():
    plot_region(rk, conf)

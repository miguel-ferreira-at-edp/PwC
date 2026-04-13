"""
Revenue por País — evolução anual, com 3 plots separados por região.
Cada subplot mostra os países dessa região (barras + linhas).

Países por região:
  Asia          → China, Japan, South Korea
  Europe        → Andorra, Austria, France, Italy, Spain, Switzerland
  North America → Canada, USA
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

country_revenue = (
    df.groupby(["Year", "Region", "Country"])["Revenue"]
    .sum()
    .reset_index()
    .sort_values(["Region", "Country", "Year"])
)

REGION_MAP = {
    "Asia":          ["China", "Japan", "South Korea"],
    "Europe":        ["Andorra", "Austria", "France", "Italy", "Spain", "Switzerland"],
    "North America": ["Canada", "USA"],
}

REGION_COLORS = {
    "Asia":          ["#1f77b4", "#aec7e8", "#08519c"],
    "Europe":        ["#ff7f0e", "#ffbb78", "#d62728", "#9467bd", "#e377c2", "#bcbd22"],
    "North America": ["#2ca02c", "#98df8a"],
}

REGION_LABELS = {
    "Asia":          "Ásia",
    "Europe":        "Europa",
    "North America": "América do Norte",
}

# ── Helper ─────────────────────────────────────────────────────────────────────
def plot_region(region_name, countries, colors, save_path):
    data = country_revenue[country_revenue["Region"] == region_name]
    years = sorted(data["Year"].unique())

    pivot = (
        data.pivot_table(index="Year", columns="Country", values="Revenue", aggfunc="sum")
        .reindex(columns=countries)
        .fillna(0)
    )

    fig, axes = plt.subplots(2, 1, figsize=(12, 11), sharex=True)
    region_label = REGION_LABELS.get(region_name, region_name)
    fig.suptitle(
        f"Revenue por País — {region_label}",
        fontsize=14, fontweight="bold", y=0.99,
    )

    # ── Barras agrupadas ───────────────────────────────────────────────────────
    ax1 = axes[0]
    n = len(countries)
    bar_w = 0.8 / n
    x = range(len(years))

    for i, (country, color) in enumerate(zip(countries, colors)):
        if country not in pivot.columns:
            continue
        offset = (i - n / 2 + 0.5) * bar_w
        ax1.bar(
            [xi + offset for xi in x],
            pivot[country],
            width=bar_w,
            label=country,
            color=color,
            alpha=0.82,
        )

    ax1.set_ylabel("Revenue", fontsize=11)
    ax1.set_title("Barras Agrupadas por País", fontsize=11)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(years)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e6:.1f}M"))
    ax1.legend(title="País", loc="upper left", fontsize=8)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    # ── Linhas ────────────────────────────────────────────────────────────────
    ax2 = axes[1]

    for country, color in zip(countries, colors):
        if country not in pivot.columns:
            continue
        ax2.plot(
            years,
            pivot[country],
            marker="o",
            linewidth=2,
            label=country,
            color=color,
        )
        last_val = pivot[country].iloc[-1]
        ax2.annotate(
            f"${last_val/1e6:.1f}M",
            xy=(years[-1], last_val),
            xytext=(5, 0),
            textcoords="offset points",
            fontsize=7.5,
            color=color,
        )

    ax2.set_xlabel("Ano", fontsize=11)
    ax2.set_ylabel("Revenue", fontsize=11)
    ax2.set_title("Linha de Tendência por País", fontsize=11)
    ax2.set_xticks(years)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e6:.1f}M"))
    ax2.legend(title="País", loc="upper left", fontsize=8)
    ax2.grid(linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"Gráfico guardado em: {save_path}")
    plt.show()


# ── Gerar os 3 plots ───────────────────────────────────────────────────────────
for region, countries in REGION_MAP.items():
    region_slug = region.lower().replace(" ", "_")
    out_path    = os.path.join(OUTPUT_DIR, f"revenue_paises_{region_slug}.png")
    plot_region(
        region_name=region,
        countries=countries,
        colors=REGION_COLORS[region],
        save_path=out_path,
    )

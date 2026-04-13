"""
Total Profit por País — 3 regiões × 3 ficheiros cada:
  _abs.png   → Stacked Area volume absoluto
  _pct.png   → Stacked Area 100% (quota no continente)
  _stats.png → Tabela de estatísticas acumuladas
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
# O ficheiro de dados foi movido para a pasta Lobão\Dados
DATA_PATH  = r"C:\Users\jfran\Documents\PwC\Lobão\Dados\sales_data_clean.csv"
OUTPUT_DIR = BASE_DIR

# ── Load & prepare ─────────────────────────────────────────────────────────────
if not os.path.exists(DATA_PATH):
    # Fallback para o caminho relativo antigo caso o absoluto falhe
    DATA_PATH = os.path.join(BASE_DIR, "..", "..", "data", "sales_data_clean.csv")

df = pd.read_csv(DATA_PATH)
# Total Profit = Sales_Price - Production_Cost - Shipping_Cost
df["Total_Profit"] = df["Sales_Price"] - df["Production_Cost"] - df["Shipping_Cost"]

country_data = (
    df.groupby(["Year", "Region", "Country"])["Total_Profit"]
    .sum()
    .reset_index()
    .sort_values(["Region", "Country", "Year"])
)

# ── Config por região ──────────────────────────────────────────────────────────
REGION_CONFIG = {
    "Asia": {
        "label":     "Ásia",
        "countries": ["China", "Japan", "South Korea"],
        "colors":    ["#1a6faf", "#4e9af1", "#a8d1f5"],
    },
    "Europe": {
        "label":     "Europa",
        "countries": ["Andorra", "Austria", "France", "Italy", "Spain", "Switzerland"],
        "colors":    ["#b35c00", "#f4a02a", "#ffd080", "#d62728", "#9467bd", "#e377c2"],
    },
    "North America": {
        "label":     "América do Norte",
        "countries": ["Canada", "USA"],
        "colors":    ["#1a7a32", "#3cba54"],
    },
}

def cagr(series):
    v0, vn = series.iloc[0], series.iloc[-1]
    if v0 <= 0:
        return float("nan")
    return ((vn / v0) ** (1 / (len(series) - 1)) - 1) * 100


def plot_region(region_key: str, config: dict):
    label     = config["label"]
    countries = config["countries"]
    colors    = config["colors"]
    n_cols    = len(countries)

    data  = country_data[country_data["Region"] == region_key]
    years = sorted(data["Year"].unique())

    pivot = (
        data.pivot_table(index="Year", columns="Country", values="Total_Profit", aggfunc="sum")
        .reindex(columns=countries)
        .fillna(0)
    )

    col_order      = pivot.sum().sort_values(ascending=False).index.tolist()
    ordered_colors = [colors[countries.index(c)] for c in col_order]
    color_map      = dict(zip(col_order, ordered_colors))
    pivot          = pivot[col_order]

    total_per_year = pivot.sum(axis=1)
    cumsum         = pivot.cumsum(axis=1)
    pivot_pct      = pivot.div(total_per_year, axis=0) * 100
    cumsum_pct     = pivot_pct.cumsum(axis=1)

    stats = {}
    for c in col_order:
        s = pivot[c]
        stats[c] = {
            "total":    s.sum(),
            "media":    s.mean(),
            "cagr":     cagr(s),
            "yoy_mean": s.pct_change().mean() * 100,
            "pico_ano": years[s.argmax()],
            "pico_val": s.max(),
            "min_ano":  years[s.argmin()],
            "min_val":  s.min(),
        }

    slug = region_key.lower().replace(" ", "_")
    MIN_FRAC      = 0.04   
    FRAC_NORMAL   = 0.13   
    FONT_SMALL    = 6.0    
    FONT_NORMAL   = 8.5    
    PCT_NORMAL    = 10     
    PCT_SMALL_MIN = 4      
    FONT_PCT_SMALL  = 6.0
    FONT_PCT_NORMAL = 9.0

    # ────────────────────────────────────────────────────────────────────────────
    # PNG 1 — Volume Absoluto
    # ────────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.suptitle(
        f"Total Profit por País — {label} (2020–2025)\nVolume Absoluto — Parcela do Continente",
        fontsize=13, fontweight="bold",
    )

    ax.stackplot(years, [pivot[c].values for c in col_order],
                 labels=col_order, colors=ordered_colors, alpha=0.87)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e6:.1f}M"))
    ax.set_xlim(years[0] - 0.3, years[-1] + 0.3)
    ax.set_xticks(years)
    ax.tick_params(axis="x", labelsize=11)
    ax.set_xlabel("Ano", fontsize=11)
    ax.set_ylabel("Total Profit", fontsize=11)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22),
              ncol=min(n_cols, 4), fontsize=10, title="País", framealpha=0.85)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.margins(y=0.15)

    for yr, tot in zip(years, total_per_year):
        ax.annotate(
            f"${tot/1e6:.1f}M",
            xy=(yr, tot),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=9, color="#111111", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor="#cccccc", alpha=0.85),
        )

    for country in col_order:
        for yr, tot_yr in zip(years, total_per_year):
            val   = pivot[country].loc[yr]
            frac  = val / tot_yr
            if frac < MIN_FRAC:
                continue
            y_mid = cumsum[country].loc[yr] - val / 2
            fs    = FONT_NORMAL if frac >= FRAC_NORMAL else FONT_SMALL
            ax.text(
                yr, y_mid,
                f"${val/1e6:.1f}M",
                ha="center", va="center",
                fontsize=fs, color="black", fontweight="bold",
            )

    plt.tight_layout()
    p = os.path.join(OUTPUT_DIR, f"total_profit_paises_{slug}_abs.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    print(f"Guardado: {p}")
    plt.close()

    # ────────────────────────────────────────────────────────────────────────────
    # PNG 2 — Quota Relativa 100% Stacked
    # ────────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.suptitle(
        f"Total Profit por País — {label} (2020–2025)\nQuota Relativa no Continente — 100% Stacked",
        fontsize=13, fontweight="bold",
    )

    ax.stackplot(years, [pivot_pct[c].values for c in col_order],
                 labels=col_order, colors=ordered_colors, alpha=0.87)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_xlim(years[0] - 0.3, years[-1] + 0.3)
    ax.set_xticks(years)
    ax.tick_params(axis="x", labelsize=11)
    ax.set_ylim(0, 110)
    ax.set_xlabel("Ano", fontsize=11)
    ax.set_ylabel("Quota no Continente (%)", fontsize=11)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.30),
              ncol=min(n_cols, 4), fontsize=10, title="País", framealpha=0.85)
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    for country in col_order:
        for yr in years:
            pct   = pivot_pct[country].loc[yr]
            if pct < PCT_SMALL_MIN:
                continue
            y_mid = cumsum_pct[country].loc[yr] - pct / 2
            fs    = FONT_PCT_NORMAL if pct >= PCT_NORMAL else FONT_PCT_SMALL
            ax.text(
                yr, y_mid,
                f"{pct:.1f}%",
                ha="center", va="center",
                fontsize=fs, color="black", fontweight="bold",
            )

    plt.tight_layout()
    p = os.path.join(OUTPUT_DIR, f"total_profit_paises_{slug}_pct.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    print(f"Guardado: {p}")
    plt.close()

    # ────────────────────────────────────────────────────────────────────────────
    # PNG 3 — Tabela de estatísticas
    # ────────────────────────────────────────────────────────────────────────────
    row_labels = [
        "Total Profit Acumulado",
        "Média Anual",
        "CAGR",
        "Cresc. Médio YoY",
        "Pico (ano)",
        "Mínimo (ano)",
    ]
    cell_data = [
        [f"${stats[c]['total']/1e6:.1f}M"                               for c in col_order],
        [f"${stats[c]['media']/1e6:.2f}M"                               for c in col_order],
        [f"{stats[c]['cagr']:.1f}%"                                     for c in col_order],
        [f"{stats[c]['yoy_mean']:.1f}%"                                 for c in col_order],
        [f"${stats[c]['pico_val']/1e6:.1f}M  ({stats[c]['pico_ano']})" for c in col_order],
        [f"${stats[c]['min_val']/1e6:.1f}M  ({stats[c]['min_ano']})"   for c in col_order],
    ]

    n_rows  = len(row_labels)
    fig_h   = 1.2 + n_rows * 0.55 + 0.6   
    fig, ax = plt.subplots(figsize=(max(8, 3.5 * n_cols + 3), fig_h))
    ax.axis("off")
    fig.suptitle(
        f"Estatísticas Acumuladas — {label} (Total Profit)",
        fontsize=13, fontweight="bold", y=0.97,
    )

    col_widths = [0.28] + [0.72 / n_cols] * n_cols

    tbl = ax.table(
        cellText=cell_data,
        rowLabels=row_labels,
        colLabels=col_order,
        cellLoc="center",
        rowLoc="left",
        loc="center",
        bbox=[0.0, 0.0, 1.0, 0.92],
        colWidths=col_widths,
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10.5 if n_cols <= 3 else 9.0)

    for j, country in enumerate(col_order):
        cell = tbl[(0, j)]
        cell.set_facecolor(color_map[country])
        cell.set_text_props(color="white", fontweight="bold")
        cell.set_edgecolor("#bbbbbb")
        cell.set_height(0.14)

    for i in range(n_rows):
        h_cell = tbl[(i + 1, -1)]
        h_cell.set_facecolor("#e8e8e8")
        h_cell.set_text_props(fontweight="bold")
        h_cell.set_edgecolor("#bbbbbb")
        h_cell.set_height(0.12)
        for j in range(n_cols):
            cell = tbl[(i + 1, j)]
            cell.set_facecolor("#f7f7f7" if i % 2 == 0 else "#ffffff")
            cell.set_edgecolor("#bbbbbb")
            cell.set_height(0.12)

    plt.tight_layout()
    p = os.path.join(OUTPUT_DIR, f"total_profit_paises_{slug}_stats.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    print(f"Guardado: {p}")
    plt.close()


# ── Gerar os 3 plots × 3 regiões = 9 ficheiros ────────────────────────────────
for region_key, config in REGION_CONFIG.items():
    plot_region(region_key, config)

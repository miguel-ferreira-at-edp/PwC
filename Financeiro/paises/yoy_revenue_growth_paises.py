"""
F07 — YoY Revenue Growth por País (3 regiões)
(Revenue_t − Revenue_t-1) / Revenue_t-1 × 100

Gera 2 ficheiros por região (6 no total):
  _bars.png   → Barras agrupadas por ano
  _stats.png  → Tabela de estatísticas acumuladas
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "..", "..", "data", "sales_data_clean.csv")
OUTPUT_DIR = BASE_DIR

# ── Load & prepare ─────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
df["Revenue"] = df["Sales_Price"]

country_annual = (
    df.groupby(["Year", "Region", "Country"])["Revenue"]
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


def plot_region(region_key: str, config: dict):
    label     = config["label"]
    countries = config["countries"]
    colors    = config["colors"]

    data  = country_annual[country_annual["Region"] == region_key].copy()

    pivot_rev = (
        data.pivot_table(index="Year", columns="Country", values="Revenue", aggfunc="sum")
        .reindex(columns=countries)
        .fillna(0)
    )

    pivot_yoy = pivot_rev.pct_change() * 100
    pivot_yoy = pivot_yoy.dropna()           # remove 1.º ano
    years     = pivot_yoy.index.tolist()

    # Ordenar por revenue total decrescente
    col_order      = pivot_rev.sum().sort_values(ascending=False).index.tolist()
    ordered_colors = [colors[countries.index(c)] for c in col_order]
    color_map      = dict(zip(col_order, ordered_colors))
    pivot_yoy      = pivot_yoy[col_order]
    n_cols         = len(col_order)
    slug           = region_key.lower().replace(" ", "_")

    # Estatísticas
    stats = {}
    for c in col_order:
        s = pivot_yoy[c]
        stats[c] = {
            "media":      s.mean(),
            "mediana":    s.median(),
            "std":        s.std(),
            "melhor_val": s.max(),
            "melhor_ano": years[s.argmax()],
            "pior_val":   s.min(),
            "pior_ano":   years[s.argmin()],
            "pos":        (s > 0).sum(),
            "n":          len(s),
        }

    # ──────────────────────────────────────────────────────────────────────────
    # PNG 1 — Barras agrupadas por ano
    # ──────────────────────────────────────────────────────────────────────────
    x       = np.arange(len(years))
    width   = 0.7 / n_cols
    offsets = np.linspace(-(n_cols - 1) / 2, (n_cols - 1) / 2, n_cols) * width

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.suptitle(
        f"YoY Revenue Growth por País — {label} (2021–2025)\nBarras Agrupadas",
        fontsize=13, fontweight="bold",
    )

    ax.axhline(0, color="#555555", linewidth=0.8, linestyle="--")

    for i, (c, col) in enumerate(zip(col_order, ordered_colors)):
        vals       = pivot_yoy[c].values
        bar_colors = [col if v >= 0 else "#d62728" for v in vals]
        bars = ax.bar(
            x + offsets[i], vals,
            width=width, color=bar_colors, alpha=0.82, label=c,
        )
        for bar, val in zip(bars, vals):
            offset = 0.4 if val >= 0 else -0.4
            va     = "bottom" if val >= 0 else "top"
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                val + offset,
                f"{val:+.1f}%",
                ha="center", va=va, fontsize=7.5,
                color=col, fontweight="bold",
            )

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:+.1f}%"))
    ax.set_xticks(x)
    ax.set_xticklabels(years, fontsize=11)
    ax.set_xlabel("Ano", fontsize=11)
    ax.set_ylabel("YoY Revenue Growth (%)", fontsize=11)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22),
              ncol=min(n_cols, 4), fontsize=10, title="País", framealpha=0.85)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.margins(y=0.20)

    plt.tight_layout()
    p = os.path.join(OUTPUT_DIR, f"yoy_revenue_growth_paises_{slug}_bars.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    print(f"Guardado: {p}")
    plt.close()

    # ──────────────────────────────────────────────────────────────────────────
    # PNG 2 — Tabela de estatísticas
    # ──────────────────────────────────────────────────────────────────────────
    row_labels = [
        "Cresc. Médio YoY",
        "Mediana YoY",
        "Desvio Padrão",
        "Melhor Ano",
        "Pior Ano",
        "Anos Positivos",
    ]
    cell_data = [
        [f"{stats[c]['media']:+.1f}%"                                               for c in col_order],
        [f"{stats[c]['mediana']:+.1f}%"                                             for c in col_order],
        [f"{stats[c]['std']:.1f} pp"                                                for c in col_order],
        [f"{stats[c]['melhor_ano']} ({stats[c]['melhor_val']:+.1f}%)"               for c in col_order],
        [f"{stats[c]['pior_ano']} ({stats[c]['pior_val']:+.1f}%)"                   for c in col_order],
        [f"{stats[c]['pos']} de {stats[c]['n']}"                                    for c in col_order],
    ]

    n_rows  = len(row_labels)
    fig_h   = 1.2 + n_rows * 0.55 + 0.6
    fig, ax = plt.subplots(figsize=(max(8, 3.5 * n_cols + 3), fig_h))
    ax.axis("off")
    fig.suptitle(
        f"Estatísticas Acumuladas — YoY Revenue Growth por País — {label}",
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

    for j, c in enumerate(col_order):
        cell = tbl[(0, j)]
        cell.set_facecolor(color_map[c])
        cell.set_text_props(color="white", fontweight="bold")
        cell.set_edgecolor("#bbbbbb")
        cell.set_height(0.14)

    for i in range(n_rows):
        tbl[(i + 1, -1)].set_facecolor("#e8e8e8")
        tbl[(i + 1, -1)].set_text_props(fontweight="bold")
        tbl[(i + 1, -1)].set_edgecolor("#bbbbbb")
        tbl[(i + 1, -1)].set_height(0.12)
        for j in range(n_cols):
            cell = tbl[(i + 1, j)]
            cell.set_facecolor("#f7f7f7" if i % 2 == 0 else "#ffffff")
            cell.set_edgecolor("#bbbbbb")
            cell.set_height(0.12)

    plt.tight_layout()
    p = os.path.join(OUTPUT_DIR, f"yoy_revenue_growth_paises_{slug}_stats.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    print(f"Guardado: {p}")
    plt.close()


# ── Gerar os 2 plots × 3 regiões = 6 ficheiros ────────────────────────────────
for region_key, config in REGION_CONFIG.items():
    plot_region(region_key, config)

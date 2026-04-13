"""
F09 — Ticket Médio por País (3 regiões)
AVG(Sales_Price)

Gera 2 ficheiros por região (6 no total):
  _bars.png   → barras agrupadas por país
  _stats.png  → tabela de estatísticas
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
df = df.dropna(subset=["Main_Category"])

country_annual = (
    df.groupby(["Year", "Region", "Country"])["Sales_Price"]
    .mean()
    .reset_index()
    .rename(columns={"Sales_Price": "Ticket"})
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
    years = sorted(data["Year"].unique())

    pivot = (
        data.pivot_table(index="Year", columns="Country", values="Ticket", aggfunc="mean")
        .reindex(columns=countries)
        .fillna(0)
    )

    col_order      = pivot.mean().sort_values(ascending=False).index.tolist()
    ordered_colors = [colors[countries.index(c)] for c in col_order]
    color_map      = dict(zip(col_order, ordered_colors))
    pivot          = pivot[col_order]
    n_cols         = len(col_order)
    slug           = region_key.lower().replace(" ", "_")

    # Estatísticas
    stats = {}
    for c in col_order:
        s   = pivot[c]
        yoy = s.pct_change() * 100
        stats[c] = {
            "media":    s.mean(),
            "max_val":  s.max(),
            "max_ano":  years[s.argmax()],
            "min_val":  s.min(),
            "min_ano":  years[s.argmin()],
            "variacao": s.iloc[-1] - s.iloc[0],
            "yoy_mean": yoy.mean(),
        }

    # ──────────────────────────────────────────────────────────────────────────
    # PNG 1 — Barras agrupadas por país
    # ──────────────────────────────────────────────────────────────────────────
    x       = np.arange(len(years))
    width   = 0.7 / n_cols
    offsets = np.linspace(-(n_cols - 1) / 2, (n_cols - 1) / 2, n_cols) * width

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.suptitle(
        f"Ticket Médio por País — {label} (2020–2025)\nBarras Agrupadas",
        fontsize=13, fontweight="bold",
    )

    for i, (c, col) in enumerate(zip(col_order, ordered_colors)):
        bars = ax.bar(
            x + offsets[i], pivot[c].values,
            width=width, color=col, alpha=0.82, label=c,
        )
        for bar, val in zip(bars, pivot[c].values):
            if val > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.4,
                    f"€{val:.0f}",
                    ha="center", va="bottom", fontsize=7.5,
                    color=col, fontweight="bold",
                )

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"€{v:.0f}"))
    ax.set_xticks(x)
    ax.set_xticklabels(years, fontsize=11)
    ax.set_xlabel("Ano", fontsize=11)
    ax.set_ylabel("Ticket Médio (€)", fontsize=11)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22),
              ncol=min(n_cols, 4), fontsize=10, title="País", framealpha=0.85)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.margins(y=0.12)

    plt.tight_layout()
    p = os.path.join(OUTPUT_DIR, f"ticket_medio_paises_{slug}_bars.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    print(f"Guardado: {p}")
    plt.close()

    # ──────────────────────────────────────────────────────────────────────────
    # PNG 2 — Tabela de estatísticas
    # ──────────────────────────────────────────────────────────────────────────
    row_labels = [
        "Ticket Médio (período)",
        "Ticket Máximo (ano)",
        "Ticket Mínimo (ano)",
        "Variação Total (€)",
        "Cresc. Médio YoY",
    ]
    cell_data = [
        [f"€{stats[c]['media']:.2f}"                                      for c in col_order],
        [f"€{stats[c]['max_val']:.2f}  ({stats[c]['max_ano']})"           for c in col_order],
        [f"€{stats[c]['min_val']:.2f}  ({stats[c]['min_ano']})"           for c in col_order],
        [f"{stats[c]['variacao']:+.2f} €"                                 for c in col_order],
        [f"{stats[c]['yoy_mean']:+.1f}%"                                  for c in col_order],
    ]

    n_rows  = len(row_labels)
    fig_h   = 1.2 + n_rows * 0.55 + 0.6
    fig, ax = plt.subplots(figsize=(max(8, 3.5 * n_cols + 3), fig_h))
    ax.axis("off")
    fig.suptitle(
        f"Estatísticas Acumuladas — Ticket Médio por País — {label}",
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
    p = os.path.join(OUTPUT_DIR, f"ticket_medio_paises_{slug}_stats.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    print(f"Guardado: {p}")
    plt.close()


# ── Gerar os 2 plots × 3 regiões = 6 ficheiros ────────────────────────────────
for region_key, config in REGION_CONFIG.items():
    plot_region(region_key, config)

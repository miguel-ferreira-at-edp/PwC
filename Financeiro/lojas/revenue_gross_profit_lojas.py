"""
Revenue e Gross Profit por Loja (Shop_ID) — evolução anual.
Gera 4 blocos de ficheiros (Revenue + Gross Profit × Absoluto + %):
  revenue_lojas_abs.png          → Stacked Area volume absoluto (Revenue)
  revenue_lojas_pct.png          → Stacked Area 100% quota (Revenue)
  revenue_lojas_stats.png        → Tabela de estatísticas (Revenue)
  gross_profit_lojas_abs.png     → Stacked Area volume absoluto (Gross Profit)
  gross_profit_lojas_pct.png     → Stacked Area 100% quota (Gross Profit)
  gross_profit_lojas_stats.png   → Tabela de estatísticas (Gross Profit)
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
df["Revenue"]      = df["Sales_Price"]
df["Gross_Profit"] = df["Sales_Price"] - df["Production_Cost"]
df = df.dropna(subset=["Shop_ID"])
df["Shop_ID"]      = df["Shop_ID"].astype(int).astype(str).apply(lambda x: f"Loja {x}")

shop_agg = (
    df.groupby(["Year", "Shop_ID"])[["Revenue", "Gross_Profit"]]
    .sum()
    .reset_index()
    .sort_values(["Shop_ID", "Year"])
)

years   = sorted(shop_agg["Year"].unique())
n_years = len(years)

# Ordenar lojas por revenue total desc
shop_order = (
    shop_agg.groupby("Shop_ID")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .index.tolist()
)
n_shops = len(shop_order)

# ── Paleta de 27 cores para as lojas ──────────────────────────────────────────
# Mix de tons distintos para garantir legibilidade
PALETTE = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
    "#aec7e8", "#ffbb78", "#98df8a", "#ff9896", "#c5b0d5",
    "#c49c94", "#f7b6d2", "#c7c7c7", "#dbdb8d", "#9edae5",
    "#393b79", "#637939", "#8c6d31", "#843c39", "#7b4173",
    "#3182bd", "#e6550d",
]
color_map = {shop: PALETTE[i % len(PALETTE)] for i, shop in enumerate(shop_order)}

# ── Helpers ────────────────────────────────────────────────────────────────────
def cagr(series):
    v0, vn = series.iloc[0], series.iloc[-1]
    if v0 <= 0:
        return float("nan")
    return ((vn / v0) ** (1 / (n_years - 1)) - 1) * 100

MIN_FRAC        = 0.04
FRAC_NORMAL     = 0.13
FONT_SMALL      = 5.5
FONT_NORMAL     = 8.0
PCT_SMALL_MIN   = 4
PCT_NORMAL      = 10
FONT_PCT_SMALL  = 5.5
FONT_PCT_NORMAL = 8.5


def make_pivot(metric: str) -> pd.DataFrame:
    return (
        shop_agg.pivot_table(index="Year", columns="Shop_ID", values=metric, aggfunc="sum")
        .reindex(columns=shop_order)
        .fillna(0)
    )


def compute_stats(pivot: pd.DataFrame) -> dict:
    stats = {}
    for shop in shop_order:
        s = pivot[shop]
        stats[shop] = {
            "total":    s.sum(),
            "media":    s.mean(),
            "cagr":     cagr(s),
            "yoy_mean": s.pct_change().mean() * 100,
            "pico_ano": years[s.argmax()],
            "pico_val": s.max(),
            "min_ano":  years[s.argmin()],
            "min_val":  s.min(),
        }
    return stats


def plot_abs(pivot, total_per_year, cumsum, metric_label: str, slug: str, title_suffix: str):
    """Stacked Area — volume absoluto."""
    fig, ax = plt.subplots(figsize=(16, 7))
    fig.suptitle(
        f"{metric_label} por Loja — Evolução Anual (2020–2025)\n{title_suffix} — Volume Absoluto",
        fontsize=13, fontweight="bold",
    )

    colors_ordered = [color_map[s] for s in shop_order]
    ax.stackplot(years, [pivot[s].values for s in shop_order],
                 labels=shop_order, colors=colors_ordered, alpha=0.87)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e6:.1f}M"))
    ax.set_xlim(years[0] - 0.3, years[-1] + 0.3)
    ax.set_xticks(years)
    ax.tick_params(axis="x", labelsize=11)
    ax.set_xlabel("Ano", fontsize=11)
    ax.set_ylabel(metric_label, fontsize=11)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.28),
              ncol=min(n_shops, 7), fontsize=8.5, title="Loja", framealpha=0.85)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.margins(y=0.15)

    # Total global no topo
    for yr, tot in zip(years, total_per_year):
        ax.annotate(
            f"${tot/1e6:.1f}M",
            xy=(yr, tot),
            xytext=(0, 10), textcoords="offset points",
            ha="center", va="bottom",
            fontsize=9, color="#111111", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor="#cccccc", alpha=0.85),
        )

    # Valor dentro de cada banda
    for shop in shop_order:
        for yr, tot_yr in zip(years, total_per_year):
            val  = pivot[shop].loc[yr]
            frac = val / tot_yr if tot_yr > 0 else 0
            if frac < MIN_FRAC:
                continue
            y_mid = cumsum[shop].loc[yr] - val / 2
            fs    = FONT_NORMAL if frac >= FRAC_NORMAL else FONT_SMALL
            ax.text(yr, y_mid, f"${val/1e6:.1f}M",
                    ha="center", va="center",
                    fontsize=fs, color="black", fontweight="bold")

    plt.tight_layout()
    p = os.path.join(OUTPUT_DIR, f"{slug}_lojas_abs.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    print(f"Guardado: {p}")
    plt.close()


def plot_pct(pivot_pct, cumsum_pct, metric_label: str, slug: str, title_suffix: str):
    """Stacked Area — quota relativa 100%."""
    fig, ax = plt.subplots(figsize=(16, 7))
    fig.suptitle(
        f"{metric_label} por Loja — Evolução Anual (2020–2025)\n{title_suffix} — Quota Relativa 100% Stacked",
        fontsize=13, fontweight="bold",
    )

    colors_ordered = [color_map[s] for s in shop_order]
    ax.stackplot(years, [pivot_pct[s].values for s in shop_order],
                 labels=shop_order, colors=colors_ordered, alpha=0.87)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_xlim(years[0] - 0.3, years[-1] + 0.3)
    ax.set_xticks(years)
    ax.tick_params(axis="x", labelsize=11)
    ax.set_ylim(0, 110)
    ax.set_xlabel("Ano", fontsize=11)
    ax.set_ylabel(f"Quota de {metric_label} (%)", fontsize=11)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.28),
              ncol=min(n_shops, 7), fontsize=8.5, title="Loja", framealpha=0.85)
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    for shop in shop_order:
        for yr in years:
            pct   = pivot_pct[shop].loc[yr]
            if pct < PCT_SMALL_MIN:
                continue
            y_mid = cumsum_pct[shop].loc[yr] - pct / 2
            fs    = FONT_PCT_NORMAL if pct >= PCT_NORMAL else FONT_PCT_SMALL
            ax.text(yr, y_mid, f"{pct:.1f}%",
                    ha="center", va="center",
                    fontsize=fs, color="black", fontweight="bold")

    plt.tight_layout()
    p = os.path.join(OUTPUT_DIR, f"{slug}_lojas_pct.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    print(f"Guardado: {p}")
    plt.close()


def plot_stats(stats, metric_label: str, slug: str):
    """Tabela de estatísticas — dividida em blocos de colunas se necessário."""
    row_labels = [
        f"{metric_label} Total Acum.",
        "Média Anual",
        "CAGR",
        "Cresc. Médio YoY",
        "Pico (ano)",
        "Mínimo (ano)",
    ]

    # Dividir em grupos de 9 lojas por tabela para legibilidade
    COLS_PER_TABLE = 9
    shop_chunks = [shop_order[i:i + COLS_PER_TABLE]
                   for i in range(0, n_shops, COLS_PER_TABLE)]

    for idx, chunk in enumerate(shop_chunks):
        n_cols  = len(chunk)
        n_rows  = len(row_labels)
        fig_h   = 1.2 + n_rows * 0.55 + 0.6
        fig, ax = plt.subplots(figsize=(max(10, 2.8 * n_cols + 3), fig_h))
        ax.axis("off")
        suffix = f" (Parte {idx + 1}/{len(shop_chunks)})" if len(shop_chunks) > 1 else ""
        fig.suptitle(
            f"Estatísticas Acumuladas por Loja — {metric_label}{suffix}",
            fontsize=13, fontweight="bold", y=0.97,
        )

        cell_data = [
            [f"${stats[c]['total']/1e6:.1f}M"                               for c in chunk],
            [f"${stats[c]['media']/1e6:.2f}M"                               for c in chunk],
            [f"{stats[c]['cagr']:.1f}%"                                      for c in chunk],
            [f"{stats[c]['yoy_mean']:.1f}%"                                  for c in chunk],
            [f"${stats[c]['pico_val']/1e6:.1f}M  ({stats[c]['pico_ano']})"  for c in chunk],
            [f"${stats[c]['min_val']/1e6:.1f}M  ({stats[c]['min_ano']})"    for c in chunk],
        ]

        col_widths = [0.28] + [0.72 / n_cols] * n_cols

        tbl = ax.table(
            cellText=cell_data,
            rowLabels=row_labels,
            colLabels=chunk,
            cellLoc="center",
            rowLoc="left",
            loc="center",
            bbox=[0.0, 0.0, 1.0, 0.92],
            colWidths=col_widths,
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(9.0 if n_cols > 6 else 10.5)

        for j, shop in enumerate(chunk):
            cell = tbl[(0, j)]
            cell.set_facecolor(color_map[shop])
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
        part_str = f"_p{idx + 1}" if len(shop_chunks) > 1 else ""
        p = os.path.join(OUTPUT_DIR, f"{slug}_lojas_stats{part_str}.png")
        plt.savefig(p, dpi=150, bbox_inches="tight")
        print(f"Guardado: {p}")
        plt.close()


# ── Revenue ────────────────────────────────────────────────────────────────────
print("── Revenue por Loja ──────────────────────────────────────────────────────")
pivot_rev          = make_pivot("Revenue")
total_rev          = pivot_rev.sum(axis=1)
cumsum_rev         = pivot_rev.cumsum(axis=1)
pivot_rev_pct      = pivot_rev.div(total_rev, axis=0) * 100
cumsum_rev_pct     = pivot_rev_pct.cumsum(axis=1)
stats_rev          = compute_stats(pivot_rev)

plot_abs(pivot_rev, total_rev, cumsum_rev,
         metric_label="Revenue", slug="revenue", title_suffix="Revenue")
plot_pct(pivot_rev_pct, cumsum_rev_pct,
         metric_label="Revenue", slug="revenue", title_suffix="Revenue")
plot_stats(stats_rev, metric_label="Revenue", slug="revenue")

# ── Gross Profit ───────────────────────────────────────────────────────────────
print("── Gross Profit por Loja ─────────────────────────────────────────────────")
pivot_gp          = make_pivot("Gross_Profit")
total_gp          = pivot_gp.sum(axis=1)
cumsum_gp         = pivot_gp.cumsum(axis=1)
pivot_gp_pct      = pivot_gp.div(total_gp, axis=0) * 100
cumsum_gp_pct     = pivot_gp_pct.cumsum(axis=1)
stats_gp          = compute_stats(pivot_gp)

plot_abs(pivot_gp, total_gp, cumsum_gp,
         metric_label="Gross Profit", slug="gross_profit", title_suffix="Gross Profit")
plot_pct(pivot_gp_pct, cumsum_gp_pct,
         metric_label="Gross Profit", slug="gross_profit", title_suffix="Gross Profit")
plot_stats(stats_gp, metric_label="Gross Profit", slug="gross_profit")

print("\nConcluído — todos os ficheiros gerados em:", OUTPUT_DIR)

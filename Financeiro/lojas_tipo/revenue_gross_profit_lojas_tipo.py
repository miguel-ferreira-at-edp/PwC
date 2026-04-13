"""
Revenue e Gross Profit por Tipo de Loja — evolução anual.

Classificação por Shop_ID:
  • Presencial  — todas as transações sem Shipping_Cost (Shipping_Cost == 0)
  • Online      — todas as transações com Shipping_Cost > 0
  • Híbrida     — misto (tem transações com e sem Shipping_Cost)

Gera 6 ficheiros:
  revenue_lojas_tipo_abs.png         → Stacked Area volume absoluto (Revenue)
  revenue_lojas_tipo_pct.png         → Stacked Area 100% quota (Revenue)
  revenue_lojas_tipo_stats.png       → Tabela de estatísticas (Revenue)
  gross_profit_lojas_tipo_abs.png    → Stacked Area volume absoluto (Gross Profit)
  gross_profit_lojas_tipo_pct.png    → Stacked Area 100% quota (Gross Profit)
  gross_profit_lojas_tipo_stats.png  → Tabela de estatísticas (Gross Profit)
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

# ── Classificar cada Shop_ID ───────────────────────────────────────────────────
def classify_shop(group):
    has_shipping    = (group["Shipping_Cost"] > 0).any()
    has_no_shipping = (group["Shipping_Cost"] == 0).any()
    if has_shipping and has_no_shipping:
        return "Híbrida"
    elif has_shipping:
        return "Online"
    else:
        return "Presencial"

shop_type_map = (
    df.groupby("Shop_ID")
    .apply(classify_shop, include_groups=False)
    .rename("Tipo_Loja")
)
df = df.join(shop_type_map, on="Shop_ID")

# ── Agregar por Ano × Tipo ─────────────────────────────────────────────────────
tipo_agg = (
    df.groupby(["Year", "Tipo_Loja"])[["Revenue", "Gross_Profit"]]
    .sum()
    .reset_index()
    .sort_values(["Tipo_Loja", "Year"])
)

years   = sorted(tipo_agg["Year"].unique())
n_years = len(years)

# Ordem e cores fixas por tipo
TYPE_ORDER  = ["Presencial", "Híbrida", "Online"]
TYPE_COLORS = {
    "Presencial": "#2ca02c",   # verde
    "Híbrida":    "#f4a02a",   # laranja
    "Online":     "#1f77b4",   # azul
}
TYPE_LABELS = {
    "Presencial": "Presencial (100% físico)",
    "Híbrida":    "Híbrida (físico + online)",
    "Online":     "Online (100% digital)",
}

# Usar apenas tipos que existem nos dados
present_types = [t for t in TYPE_ORDER if t in tipo_agg["Tipo_Loja"].unique()]
n_types       = len(present_types)

# ── Helpers ────────────────────────────────────────────────────────────────────
def cagr(series):
    v0, vn = series.iloc[0], series.iloc[-1]
    if v0 <= 0:
        return float("nan")
    return ((vn / v0) ** (1 / (n_years - 1)) - 1) * 100

MIN_FRAC        = 0.04
FRAC_NORMAL     = 0.13
FONT_SMALL      = 6.0
FONT_NORMAL     = 8.5
PCT_SMALL_MIN   = 4
PCT_NORMAL      = 10
FONT_PCT_SMALL  = 6.0
FONT_PCT_NORMAL = 9.0


def make_pivot(metric: str) -> pd.DataFrame:
    return (
        tipo_agg.pivot_table(index="Year", columns="Tipo_Loja", values=metric, aggfunc="sum")
        .reindex(columns=present_types)
        .fillna(0)
    )


def compute_stats(pivot: pd.DataFrame) -> dict:
    stats = {}
    for t in present_types:
        s = pivot[t]
        stats[t] = {
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


def plot_abs(pivot, total_per_year, cumsum, metric_label: str, slug: str):
    """Stacked Area — volume absoluto."""
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.suptitle(
        f"{metric_label} por Tipo de Loja — Evolução Anual (2020–2025)\nVolume Absoluto",
        fontsize=13, fontweight="bold",
    )

    colors  = [TYPE_COLORS[t] for t in present_types]
    labels  = [TYPE_LABELS[t] for t in present_types]

    ax.stackplot(years, [pivot[t].values for t in present_types],
                 labels=labels, colors=colors, alpha=0.87)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e6:.1f}M"))
    ax.set_xlim(years[0] - 0.3, years[-1] + 0.3)
    ax.set_xticks(years)
    ax.tick_params(axis="x", labelsize=11)
    ax.set_xlabel("Ano", fontsize=11)
    ax.set_ylabel(metric_label, fontsize=11)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22),
              ncol=min(n_types, 4), fontsize=10, title="Tipo de Loja", framealpha=0.85)
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
    for tipo in present_types:
        for yr, tot_yr in zip(years, total_per_year):
            val  = pivot[tipo].loc[yr]
            frac = val / tot_yr if tot_yr > 0 else 0
            if frac < MIN_FRAC:
                continue
            y_mid = cumsum[tipo].loc[yr] - val / 2
            fs    = FONT_NORMAL if frac >= FRAC_NORMAL else FONT_SMALL
            ax.text(yr, y_mid, f"${val/1e6:.1f}M",
                    ha="center", va="center",
                    fontsize=fs, color="black", fontweight="bold")

    plt.tight_layout()
    p = os.path.join(OUTPUT_DIR, f"{slug}_lojas_tipo_abs.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    print(f"Guardado: {p}")
    plt.close()


def plot_pct(pivot_pct, cumsum_pct, metric_label: str, slug: str):
    """Stacked Area — quota relativa 100%."""
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.suptitle(
        f"{metric_label} por Tipo de Loja — Evolução Anual (2020–2025)\nQuota Relativa — 100% Stacked",
        fontsize=13, fontweight="bold",
    )

    colors = [TYPE_COLORS[t] for t in present_types]
    labels = [TYPE_LABELS[t] for t in present_types]

    ax.stackplot(years, [pivot_pct[t].values for t in present_types],
                 labels=labels, colors=colors, alpha=0.87)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_xlim(years[0] - 0.3, years[-1] + 0.3)
    ax.set_xticks(years)
    ax.tick_params(axis="x", labelsize=11)
    ax.set_ylim(0, 110)
    ax.set_xlabel("Ano", fontsize=11)
    ax.set_ylabel(f"Quota de {metric_label} (%)", fontsize=11)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22),
              ncol=min(n_types, 4), fontsize=10, title="Tipo de Loja", framealpha=0.85)
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    for tipo in present_types:
        for yr in years:
            pct   = pivot_pct[tipo].loc[yr]
            if pct < PCT_SMALL_MIN:
                continue
            y_mid = cumsum_pct[tipo].loc[yr] - pct / 2
            fs    = FONT_PCT_NORMAL if pct >= PCT_NORMAL else FONT_PCT_SMALL
            ax.text(yr, y_mid, f"{pct:.1f}%",
                    ha="center", va="center",
                    fontsize=fs, color="black", fontweight="bold")

    plt.tight_layout()
    p = os.path.join(OUTPUT_DIR, f"{slug}_lojas_tipo_pct.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    print(f"Guardado: {p}")
    plt.close()


def plot_stats(stats, metric_label: str, slug: str):
    """Tabela de estatísticas."""
    row_labels = [
        f"{metric_label} Total Acum.",
        "Média Anual",
        "CAGR",
        "Cresc. Médio YoY",
        "Pico (ano)",
        "Mínimo (ano)",
    ]
    col_labels = [TYPE_LABELS[t] for t in present_types]
    cell_data  = [
        [f"${stats[t]['total']/1e6:.1f}M"                               for t in present_types],
        [f"${stats[t]['media']/1e6:.2f}M"                               for t in present_types],
        [f"{stats[t]['cagr']:.1f}%"                                      for t in present_types],
        [f"{stats[t]['yoy_mean']:.1f}%"                                  for t in present_types],
        [f"${stats[t]['pico_val']/1e6:.1f}M  ({stats[t]['pico_ano']})"  for t in present_types],
        [f"${stats[t]['min_val']/1e6:.1f}M  ({stats[t]['min_ano']})"    for t in present_types],
    ]

    n_rows  = len(row_labels)
    fig_h   = 1.2 + n_rows * 0.55 + 0.6
    fig, ax = plt.subplots(figsize=(max(10, 3.5 * n_types + 3), fig_h))
    ax.axis("off")
    fig.suptitle(
        f"Estatísticas Acumuladas por Tipo de Loja — {metric_label}",
        fontsize=13, fontweight="bold", y=0.97,
    )

    col_widths = [0.28] + [0.72 / n_types] * n_types

    tbl = ax.table(
        cellText=cell_data,
        rowLabels=row_labels,
        colLabels=col_labels,
        cellLoc="center",
        rowLoc="left",
        loc="center",
        bbox=[0.0, 0.0, 1.0, 0.92],
        colWidths=col_widths,
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10.5)

    for j, tipo in enumerate(present_types):
        cell = tbl[(0, j)]
        cell.set_facecolor(TYPE_COLORS[tipo])
        cell.set_text_props(color="white", fontweight="bold")
        cell.set_edgecolor("#bbbbbb")
        cell.set_height(0.14)

    for i in range(n_rows):
        h_cell = tbl[(i + 1, -1)]
        h_cell.set_facecolor("#e8e8e8")
        h_cell.set_text_props(fontweight="bold")
        h_cell.set_edgecolor("#bbbbbb")
        h_cell.set_height(0.12)
        for j in range(n_types):
            cell = tbl[(i + 1, j)]
            cell.set_facecolor("#f7f7f7" if i % 2 == 0 else "#ffffff")
            cell.set_edgecolor("#bbbbbb")
            cell.set_height(0.12)

    plt.tight_layout()
    p = os.path.join(OUTPUT_DIR, f"{slug}_lojas_tipo_stats.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    print(f"Guardado: {p}")
    plt.close()


# ── Mostrar contagem de lojas por tipo ────────────────────────────────────────
print("── Classificação de Lojas ────────────────────────────────────────────────")
for t in present_types:
    shops = shop_type_map[shop_type_map == t].index.tolist()
    print(f"  {TYPE_LABELS[t]:35s}: {len(shops):3d} loja(s) — IDs: {shops}")
print()

# ── Revenue ────────────────────────────────────────────────────────────────────
print("── Revenue por Tipo de Loja ──────────────────────────────────────────────")
pivot_rev      = make_pivot("Revenue")
total_rev      = pivot_rev.sum(axis=1)
cumsum_rev     = pivot_rev.cumsum(axis=1)
pivot_rev_pct  = pivot_rev.div(total_rev, axis=0) * 100
cumsum_rev_pct = pivot_rev_pct.cumsum(axis=1)
stats_rev      = compute_stats(pivot_rev)

plot_abs(pivot_rev, total_rev, cumsum_rev,
         metric_label="Revenue", slug="revenue")
plot_pct(pivot_rev_pct, cumsum_rev_pct,
         metric_label="Revenue", slug="revenue")
plot_stats(stats_rev, metric_label="Revenue", slug="revenue")

# ── Gross Profit ───────────────────────────────────────────────────────────────
print("── Gross Profit por Tipo de Loja ─────────────────────────────────────────")
pivot_gp      = make_pivot("Gross_Profit")
total_gp      = pivot_gp.sum(axis=1)
cumsum_gp     = pivot_gp.cumsum(axis=1)
pivot_gp_pct  = pivot_gp.div(total_gp, axis=0) * 100
cumsum_gp_pct = pivot_gp_pct.cumsum(axis=1)
stats_gp      = compute_stats(pivot_gp)

plot_abs(pivot_gp, total_gp, cumsum_gp,
         metric_label="Gross Profit", slug="gross_profit")
plot_pct(pivot_gp_pct, cumsum_gp_pct,
         metric_label="Gross Profit", slug="gross_profit")
plot_stats(stats_gp, metric_label="Gross Profit", slug="gross_profit")

print("\nConcluído — todos os ficheiros gerados em:", OUTPUT_DIR)

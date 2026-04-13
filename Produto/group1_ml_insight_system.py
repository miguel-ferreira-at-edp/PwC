from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = ROOT / "data" / "sales_data_clean.csv"
DEFAULT_OUTPUT_DIR = ROOT / "Produto" / "ml_group1_outputs"
RANDOM_STATE = 42


@dataclass
class ModelResult:
    name: str
    target: str
    metrics: dict[str, float]
    importances: pd.DataFrame
    predictions: pd.Series


def safe_divide(numerator: pd.Series | np.ndarray, denominator: pd.Series | np.ndarray) -> np.ndarray:
    numerator = np.asarray(numerator, dtype=float)
    denominator = np.asarray(denominator, dtype=float)
    return np.divide(numerator, denominator, out=np.zeros_like(numerator, dtype=float), where=denominator != 0)


def scale_minmax(series: pd.Series, reverse: bool = False) -> pd.Series:
    values = series.astype(float)
    min_value = values.min()
    max_value = values.max()
    if np.isclose(min_value, max_value):
        scaled = pd.Series(np.zeros(len(values)), index=values.index)
    else:
        scaled = (values - min_value) / (max_value - min_value)
    if reverse:
        scaled = 1 - scaled
    return scaled.clip(0, 1)


class Group1MLInsightSystem:
    def __init__(self, data_path: Path = DEFAULT_DATA_PATH, output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_orders(self) -> pd.DataFrame:
        df = pd.read_csv(self.data_path, parse_dates=["Order_Date", "Due_Date"])

        essential_categoricals = ["Region", "Country", "Main_Category", "Subcategory", "Product_ID"]
        for column in essential_categoricals:
            df[column] = df[column].fillna("Unknown")

        df["Quarter"] = df["Order_Date"].dt.quarter.astype(int)
        df["Month"] = df["Order_Date"].dt.month.astype(int)
        df["delivery_days"] = (df["Due_Date"] - df["Order_Date"]).dt.days.fillna(0).clip(lower=0)
        df["shop_age"] = (df["Year"] - df["Year_Opened"]).fillna(0).clip(lower=0)
        df["profit"] = df["Sales_Price"] - df["Production_Cost"] - df["Shipping_Cost"]
        df["profit_margin_pct"] = safe_divide(df["profit"], df["Sales_Price"])
        df["shipping_ratio"] = safe_divide(df["Shipping_Cost"], df["Sales_Price"])
        df["production_ratio"] = safe_divide(df["Production_Cost"], df["Sales_Price"])

        return df

    def build_segments(self, orders: pd.DataFrame) -> pd.DataFrame:
        segment_cols = ["Year", "Quarter", "Region", "Country", "Main_Category", "Subcategory"]

        segment = (
            orders.groupby(segment_cols, dropna=False)
            .agg(
                orders=("Sales_Order_ID", "count"),
                revenue=("Sales_Price", "sum"),
                production_cost=("Production_Cost", "sum"),
                shipping_cost=("Shipping_Cost", "sum"),
                profit=("profit", "sum"),
                avg_sales_price=("Sales_Price", "mean"),
                avg_delivery_days=("delivery_days", "mean"),
                has_shipping_rate=("Has_Shipping", "mean"),
                avg_shop_age=("shop_age", "mean"),
                unique_products=("Product_ID", "nunique"),
            )
            .reset_index()
        )

        product_revenue = (
            orders.groupby(segment_cols + ["Product_ID"], dropna=False)["Sales_Price"]
            .sum()
            .reset_index(name="product_revenue")
        )
        product_revenue["segment_revenue"] = product_revenue.groupby(segment_cols)["product_revenue"].transform("sum")
        product_revenue["product_revenue_share"] = safe_divide(
            product_revenue["product_revenue"], product_revenue["segment_revenue"]
        )
        concentration = (
            product_revenue.groupby(segment_cols)["product_revenue_share"].max().reset_index(name="top_product_revenue_share")
        )

        segment = segment.merge(concentration, on=segment_cols, how="left")
        segment["profit_margin_pct"] = safe_divide(segment["profit"], segment["revenue"])
        segment["shipping_ratio"] = safe_divide(segment["shipping_cost"], segment["revenue"])
        segment["production_ratio"] = safe_divide(segment["production_cost"], segment["revenue"])
        segment["profit_per_order"] = safe_divide(segment["profit"], segment["orders"])
        segment["revenue_per_order"] = safe_divide(segment["revenue"], segment["orders"])

        segment["revenue_share_country_quarter"] = safe_divide(
            segment["revenue"], segment.groupby(["Year", "Quarter", "Country"])["revenue"].transform("sum")
        )
        segment["profit_share_region_quarter"] = safe_divide(
            segment["profit"], segment.groupby(["Year", "Quarter", "Region"])["profit"].transform("sum")
        )

        growth_keys = ["Country", "Main_Category", "Subcategory", "Quarter"]
        segment = segment.sort_values(growth_keys + ["Year"]).reset_index(drop=True)
        segment["profit_yoy_growth"] = (
            segment.groupby(growth_keys)["profit"].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0)
        )
        segment["orders_yoy_growth"] = (
            segment.groupby(growth_keys)["orders"].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0)
        )

        region_baseline = (
            segment.groupby(["Year", "Quarter", "Region"])
            .agg(region_margin_pct=("profit_margin_pct", "mean"), region_shipping_ratio=("shipping_ratio", "mean"))
            .reset_index()
        )
        segment = segment.merge(region_baseline, on=["Year", "Quarter", "Region"], how="left")
        segment["margin_gap_vs_region"] = segment["profit_margin_pct"] - segment["region_margin_pct"]
        segment["shipping_gap_vs_region"] = segment["shipping_ratio"] - segment["region_shipping_ratio"]

        return segment

    def fit_regression_model(
        self,
        df: pd.DataFrame,
        target: str,
        feature_columns: list[str],
        model_name: str,
    ) -> tuple[ModelResult, Pipeline]:
        train_mask = df["Year"] < 2025
        test_mask = df["Year"] == 2025

        train_df = df.loc[train_mask].copy()
        test_df = df.loc[test_mask].copy()

        categorical_cols = [column for column in feature_columns if df[column].dtype == "object"]
        numeric_cols = [column for column in feature_columns if column not in categorical_cols]

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "cat",
                    Pipeline(
                        steps=[
                            ("imputer", SimpleImputer(strategy="most_frequent")),
                            ("encoder", OneHotEncoder(handle_unknown="ignore")),
                        ]
                    ),
                    categorical_cols,
                ),
                (
                    "num",
                    Pipeline(
                        steps=[
                            ("imputer", SimpleImputer(strategy="median")),
                            ("scaler", StandardScaler()),
                        ]
                    ),
                    numeric_cols,
                ),
            ]
        )

        model = RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=3,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )

        pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])
        pipeline.fit(train_df[feature_columns], train_df[target])

        test_pred = pipeline.predict(test_df[feature_columns])
        all_pred = pipeline.predict(df[feature_columns])

        metrics = {
            "mae": float(mean_absolute_error(test_df[target], test_pred)),
            "rmse": float(np.sqrt(mean_squared_error(test_df[target], test_pred))),
            "r2": float(r2_score(test_df[target], test_pred)),
        }

        importance = permutation_importance(
            pipeline,
            test_df[feature_columns],
            test_df[target],
            n_repeats=10,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
        importance_df = pd.DataFrame(
            {
                "feature": feature_columns,
                "importance_mean": importance.importances_mean,
                "importance_std": importance.importances_std,
                "model": model_name,
                "target": target,
            }
        ).sort_values("importance_mean", ascending=False)

        result = ModelResult(
            name=model_name,
            target=target,
            metrics=metrics,
            importances=importance_df.reset_index(drop=True),
            predictions=pd.Series(all_pred, index=df.index, name=f"pred_{target}"),
        )
        return result, pipeline

    def choose_cluster_count(self, features: pd.DataFrame) -> int:
        best_k = 4
        best_score = -1.0

        for k in range(3, 7):
            model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=20)
            labels = model.fit_predict(features)
            score = silhouette_score(features, labels)
            if score > best_score:
                best_k = k
                best_score = score

        return best_k

    def label_cluster_profiles(self, profile_df: pd.DataFrame) -> pd.DataFrame:
        global_margin = profile_df["profit_margin_pct"].median()
        global_shipping = profile_df["shipping_ratio"].median()
        global_profit_per_order = profile_df["profit_per_order"].median()
        global_growth = profile_df["profit_yoy_growth"].median()

        labels: list[str] = []
        for _, row in profile_df.iterrows():
            if row["profit_margin_pct"] >= global_margin and row["profit_per_order"] >= global_profit_per_order and row["margin_gap_vs_model"] >= 0:
                labels.append("Core rentavel")
            elif row["shipping_ratio"] >= global_shipping * 1.2 and row["shipping_gap_vs_model"] > 0:
                labels.append("Pressao logistica")
            elif row["profit_margin_pct"] < global_margin and row["profit_per_order"] < global_profit_per_order:
                labels.append("Cauda de baixo valor")
            elif row["profit_yoy_growth"] > global_growth and row["margin_gap_vs_model"] >= 0:
                labels.append("Bolsa de crescimento")
            else:
                labels.append("Perfil misto")

        profile_df = profile_df.copy()
        profile_df["cluster_label"] = labels
        return profile_df

    def assign_anomaly_reasons(self, segments: pd.DataFrame) -> pd.Series:
        thresholds = {
            "low_margin": segments["profit_margin_pct"].quantile(0.25),
            "negative_gap": segments["margin_gap_vs_model"].quantile(0.15),
            "high_shipping": segments["shipping_ratio"].quantile(0.75),
            "high_shipping_gap": segments["shipping_gap_vs_model"].quantile(0.75),
            "high_concentration": segments["top_product_revenue_share"].quantile(0.75),
            "low_growth": segments["profit_yoy_growth"].quantile(0.25),
        }

        reasons: list[str] = []
        for _, row in segments.iterrows():
            row_reasons: list[str] = []
            if row["profit_margin_pct"] <= thresholds["low_margin"]:
                row_reasons.append("margem baixa")
            if row["margin_gap_vs_model"] <= thresholds["negative_gap"]:
                row_reasons.append("abaixo do esperado pelo modelo")
            if row["shipping_ratio"] >= thresholds["high_shipping"]:
                row_reasons.append("pressao de shipping")
            if row["shipping_gap_vs_model"] >= thresholds["high_shipping_gap"]:
                row_reasons.append("shipping acima do esperado")
            if row["top_product_revenue_share"] >= thresholds["high_concentration"]:
                row_reasons.append("dependencia de poucos SKUs")
            if row["profit_yoy_growth"] <= thresholds["low_growth"]:
                row_reasons.append("crescimento fraco")

            reasons.append(", ".join(row_reasons[:3]) if row_reasons else "perfil anomalo composto")

        return pd.Series(reasons, index=segments.index)

    def cluster_and_detect_anomalies(self, segments: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, int]:
        cluster_features = [
            "profit_margin_pct",
            "shipping_ratio",
            "production_ratio",
            "profit_per_order",
            "revenue_per_order",
            "has_shipping_rate",
            "avg_delivery_days",
            "top_product_revenue_share",
            "profit_yoy_growth",
            "orders_yoy_growth",
            "margin_gap_vs_model",
            "shipping_gap_vs_model",
            "risk_score",
        ]

        scaler = StandardScaler()
        scaled = scaler.fit_transform(segments[cluster_features].fillna(0))
        scaled_df = pd.DataFrame(scaled, columns=cluster_features, index=segments.index)

        best_k = self.choose_cluster_count(scaled_df)
        kmeans = KMeans(n_clusters=best_k, random_state=RANDOM_STATE, n_init=20)
        segments = segments.copy()
        segments["cluster_id"] = kmeans.fit_predict(scaled_df)

        profile = (
            segments.groupby("cluster_id")
            .agg(
                segment_count=("cluster_id", "size"),
                revenue=("revenue", "sum"),
                profit=("profit", "sum"),
                profit_margin_pct=("profit_margin_pct", "mean"),
                shipping_ratio=("shipping_ratio", "mean"),
                profit_per_order=("profit_per_order", "mean"),
                profit_yoy_growth=("profit_yoy_growth", "mean"),
                margin_gap_vs_model=("margin_gap_vs_model", "mean"),
                shipping_gap_vs_model=("shipping_gap_vs_model", "mean"),
                risk_score=("risk_score", "mean"),
            )
            .reset_index()
        )
        profile["revenue_share_pct"] = safe_divide(profile["revenue"], profile["revenue"].sum())
        profile = self.label_cluster_profiles(profile)
        cluster_label_map = dict(zip(profile["cluster_id"], profile["cluster_label"]))
        segments["cluster_label"] = segments["cluster_id"].map(cluster_label_map)

        isolation = IsolationForest(contamination=0.08, random_state=RANDOM_STATE)
        isolation.fit(scaled_df)
        segments["anomaly_flag"] = isolation.predict(scaled_df)
        segments["anomaly_score"] = -isolation.decision_function(scaled_df)
        segments["anomaly_reason"] = self.assign_anomaly_reasons(segments)

        return segments, profile.sort_values("revenue", ascending=False), best_k

    def build_geography_watchlist(self, segments: pd.DataFrame) -> pd.DataFrame:
        geo_year = (
            segments.groupby(["Region", "Country", "Year"])
            .agg(
                revenue=("revenue", "sum"),
                profit=("profit", "sum"),
                profit_margin_pct=("profit_margin_pct", "mean"),
                shipping_ratio=("shipping_ratio", "mean"),
                margin_gap_vs_model=("margin_gap_vs_model", "mean"),
                shipping_gap_vs_model=("shipping_gap_vs_model", "mean"),
                anomaly_rate=("anomaly_flag", lambda x: (x == -1).mean()),
                risk_score=("risk_score", "mean"),
            )
            .reset_index()
        )
        geo_year = geo_year.loc[geo_year["Country"] != "Unknown"].copy()

        geo_year["risk_rank"] = geo_year["risk_score"].rank(ascending=False, method="dense").astype(int)

        country_watchlist = (
            geo_year.groupby(["Region", "Country"])
            .agg(
                revenue=("revenue", "sum"),
                profit=("profit", "sum"),
                profit_margin_pct=("profit_margin_pct", "mean"),
                shipping_ratio=("shipping_ratio", "mean"),
                margin_gap_vs_model=("margin_gap_vs_model", "mean"),
                shipping_gap_vs_model=("shipping_gap_vs_model", "mean"),
                anomaly_rate=("anomaly_rate", "mean"),
                risk_score=("risk_score", "mean"),
            )
            .reset_index()
            .sort_values("risk_score", ascending=False)
        )
        country_watchlist["watchlist_rank"] = range(1, len(country_watchlist) + 1)
        return geo_year, country_watchlist

    def write_plots(self, geo_year: pd.DataFrame, segments: pd.DataFrame) -> None:
        heatmap_source = geo_year.copy()
        heatmap_source["geo_label"] = heatmap_source["Region"] + " | " + heatmap_source["Country"]
        heatmap = heatmap_source.pivot(index="geo_label", columns="Year", values="risk_score").sort_index()
        plt.figure(figsize=(10, 6))
        image = plt.imshow(heatmap.values, aspect="auto", cmap="YlOrRd")
        plt.colorbar(image, label="Risk score")
        plt.xticks(range(len(heatmap.columns)), heatmap.columns)
        plt.yticks(range(len(heatmap.index)), heatmap.index)
        plt.title("Group 1 ML: geography risk heatmap")
        plt.tight_layout()
        plt.savefig(self.output_dir / "group1_geography_risk_heatmap.png", dpi=180)
        plt.close()

        plt.figure(figsize=(10, 6))
        for cluster_label, subset in segments.groupby("cluster_label"):
            plt.scatter(
                subset["shipping_ratio"],
                subset["profit_margin_pct"],
                s=np.clip(subset["revenue"] / 700, 15, 220),
                alpha=0.65,
                label=cluster_label,
            )
        plt.axhline(segments["profit_margin_pct"].median(), color="grey", linestyle="--", linewidth=1)
        plt.axvline(segments["shipping_ratio"].median(), color="grey", linestyle="--", linewidth=1)
        plt.xlabel("Shipping ratio")
        plt.ylabel("Profit margin pct")
        plt.title("Group 1 ML: segment clusters")
        plt.legend()
        plt.tight_layout()
        plt.savefig(self.output_dir / "group1_segment_clusters.png", dpi=180)
        plt.close()

    def build_report(
        self,
        margin_result: ModelResult,
        shipping_result: ModelResult,
        cluster_profiles: pd.DataFrame,
        anomalies: pd.DataFrame,
        country_watchlist: pd.DataFrame,
        anomaly_country_summary: pd.DataFrame,
        best_k: int,
    ) -> str:
        top_margin_features = margin_result.importances.head(5)["feature"].tolist()
        top_shipping_features = shipping_result.importances.head(5)["feature"].tolist()

        top_country = country_watchlist.iloc[0]
        safest_country = country_watchlist.iloc[-1]
        biggest_cluster = cluster_profiles.sort_values("revenue", ascending=False).iloc[0]
        riskiest_cluster = cluster_profiles.sort_values("risk_score", ascending=False).iloc[0]
        anomaly_country = anomaly_country_summary.iloc[0]

        anomaly_lines = []
        for _, row in anomalies.head(5).iterrows():
            anomaly_lines.append(
                f"- {row['Country']} | {int(row['Year'])} Q{int(row['Quarter'])} | "
                f"{row['Subcategory']} | risk {row['risk_score']:.1f} | {row['anomaly_reason']}"
            )

        report = f"""# Group 1 ML Insight System

## Objetivo
Criar um sistema de ML para apoiar o Grupo 1 do enunciado:
- diagnosticar a performance das geografias;
- identificar constrangimentos relevantes;
- transformar o diagnostico em watchlists e insights acionaveis.

## Algoritmos usados
- Random Forest Regressor para estimar `profit_margin_pct`
- Random Forest Regressor para estimar `shipping_ratio`
- KMeans para descobrir arquetipos de segmentos
- Isolation Forest para detetar segmentos anormais

## Performance dos modelos
- Modelo estrutural de margem: R2 {margin_result.metrics['r2']:.3f} | RMSE {margin_result.metrics['rmse']:.4f} | MAE {margin_result.metrics['mae']:.4f}
- Modelo de shipping: R2 {shipping_result.metrics['r2']:.3f} | RMSE {shipping_result.metrics['rmse']:.4f} | MAE {shipping_result.metrics['mae']:.4f}

## Drivers mais relevantes
- Drivers do modelo estrutural de margem: {", ".join(top_margin_features)}
- Drivers do modelo de shipping: {", ".join(top_shipping_features)}

## Principais sinais encontrados
- Geografia mais critica no watchlist: {top_country['Country']} ({top_country['Region']}) com risk score medio de {top_country['risk_score']:.1f}, margem media de {top_country['profit_margin_pct']:.3f} e shipping ratio medio de {top_country['shipping_ratio']:.3f}.
- Geografia mais robusta no watchlist: {safest_country['Country']} ({safest_country['Region']}) com risk score medio de {safest_country['risk_score']:.1f}.
- O cluster com maior peso de receita e "{biggest_cluster['cluster_label']}" e representa {biggest_cluster['revenue_share_pct'] * 100:.1f}% da receita dos segmentos analisados.
- O cluster mais arriscado e "{riskiest_cluster['cluster_label']}" com risk score medio de {riskiest_cluster['risk_score']:.1f}.
- A maior concentracao de anomalias esta em {anomaly_country['Country']} ({anomaly_country['Region']}), com {int(anomaly_country['anomaly_count'])} segmentos anormais, ou {anomaly_country['anomaly_share_pct']:.1f}% do total.
- O numero de clusters escolhido pelo sistema foi {best_k}.

## Anomalias prioritarias
{chr(10).join(anomaly_lines)}

## Como usar na apresentacao
- Usar o watchlist por pais para sustentar a parte de diagnostico geografico.
- Usar os drivers do modelo para separar causas estruturais (produto/geografia) de causas operacionais (shipping e concentracao).
- Usar clusters e anomalias para mostrar onde estao os segmentos que fogem ao padrao esperado e exigem acao.

## Ficheiros gerados
- `margin_model_feature_importance.csv`
- `shipping_model_feature_importance.csv`
- `segment_ml_scores.csv`
- `segment_cluster_profiles.csv`
- `segment_anomalies.csv`
- `country_anomaly_summary.csv`
- `country_watchlist.csv`
- `geography_year_watchlist.csv`
- `group1_geography_risk_heatmap.png`
- `group1_segment_clusters.png`
"""
        return report

    def run(self) -> dict[str, float | int | str]:
        orders = self.load_orders()
        segments = self.build_segments(orders)
        segments = segments.loc[segments["orders"] >= 5].copy()

        feature_columns = [
            "Region",
            "Country",
            "Main_Category",
            "Subcategory",
            "Quarter",
            "Year",
            "orders",
            "avg_sales_price",
            "has_shipping_rate",
            "avg_delivery_days",
            "avg_shop_age",
            "unique_products",
            "top_product_revenue_share",
            "orders_yoy_growth",
        ]

        margin_result, _ = self.fit_regression_model(
            segments,
            target="profit_margin_pct",
            feature_columns=feature_columns,
            model_name="margin_model",
        )
        shipping_result, _ = self.fit_regression_model(
            segments,
            target="shipping_ratio",
            feature_columns=feature_columns,
            model_name="shipping_model",
        )

        segments["pred_profit_margin_pct"] = margin_result.predictions
        segments["pred_shipping_ratio"] = shipping_result.predictions
        segments["margin_gap_vs_model"] = segments["profit_margin_pct"] - segments["pred_profit_margin_pct"]
        segments["shipping_gap_vs_model"] = segments["shipping_ratio"] - segments["pred_shipping_ratio"]

        segments["risk_score"] = 100 * (
            0.30 * scale_minmax(segments["profit_margin_pct"], reverse=True)
            + 0.20 * scale_minmax(segments["margin_gap_vs_model"], reverse=True)
            + 0.20 * scale_minmax(segments["shipping_ratio"])
            + 0.10 * scale_minmax(segments["shipping_gap_vs_model"])
            + 0.10 * scale_minmax(segments["top_product_revenue_share"])
            + 0.10 * scale_minmax(segments["profit_yoy_growth"], reverse=True)
        )

        segments, cluster_profiles, best_k = self.cluster_and_detect_anomalies(segments)

        anomalies = (
            segments.loc[segments["anomaly_flag"] == -1]
            .sort_values(["risk_score", "anomaly_score"], ascending=False)
            .copy()
        )
        anomaly_country_summary = (
            anomalies.groupby(["Region", "Country"])
            .size()
            .reset_index(name="anomaly_count")
            .sort_values("anomaly_count", ascending=False)
        )
        anomaly_country_summary["anomaly_share_pct"] = safe_divide(
            anomaly_country_summary["anomaly_count"], anomaly_country_summary["anomaly_count"].sum()
        ) * 100
        geo_year, country_watchlist = self.build_geography_watchlist(segments)
        self.write_plots(geo_year, segments)

        margin_result.importances.to_csv(self.output_dir / "margin_model_feature_importance.csv", index=False)
        shipping_result.importances.to_csv(self.output_dir / "shipping_model_feature_importance.csv", index=False)
        segments.sort_values("risk_score", ascending=False).to_csv(self.output_dir / "segment_ml_scores.csv", index=False)
        cluster_profiles.to_csv(self.output_dir / "segment_cluster_profiles.csv", index=False)
        anomalies.to_csv(self.output_dir / "segment_anomalies.csv", index=False)
        anomaly_country_summary.to_csv(self.output_dir / "country_anomaly_summary.csv", index=False)
        country_watchlist.to_csv(self.output_dir / "country_watchlist.csv", index=False)
        geo_year.to_csv(self.output_dir / "geography_year_watchlist.csv", index=False)

        model_metrics = {
            "margin_model": margin_result.metrics,
            "shipping_model": shipping_result.metrics,
            "cluster_count": best_k,
            "segment_count": int(len(segments)),
            "anomaly_count": int(len(anomalies)),
        }
        (self.output_dir / "model_metrics.json").write_text(json.dumps(model_metrics, indent=2))

        report = self.build_report(
            margin_result=margin_result,
            shipping_result=shipping_result,
            cluster_profiles=cluster_profiles,
            anomalies=anomalies,
            country_watchlist=country_watchlist,
            anomaly_country_summary=anomaly_country_summary,
            best_k=best_k,
        )
        (self.output_dir / "group1_ml_report.md").write_text(report)

        return {
            "output_dir": str(self.output_dir),
            "segment_count": int(len(segments)),
            "anomaly_count": int(len(anomalies)),
            "cluster_count": int(best_k),
            "margin_r2": margin_result.metrics["r2"],
            "shipping_r2": shipping_result.metrics["r2"],
        }


def main() -> None:
    system = Group1MLInsightSystem()
    summary = system.run()
    print("=== Group 1 ML Insight System ===")
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()

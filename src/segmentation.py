"""Reproduceerbare klantsegmentatie met scikit-learn."""

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.analysis import rfm_segments


CLUSTER_NAMES = [
    "High-value regulars",
    "Growth opportunity",
    "Occasional customers",
    "Re-engagement opportunity",
]


def cluster_customers(data: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    """Cluster klanten op RFM-gedrag en geef een uitlegbare segmentnaam terug.

    K-Means werkt op afstand. We schalen recency, frequency en monetary daarom
    eerst naar dezelfde schaal; anders zou euro-omzet alle andere signalen
    overheersen. De uiteindelijke namen worden bepaald door de gemiddelde
    klantwaarde per cluster, want K-Means-clusternummers zelf zijn willekeurig.
    """
    rfm = rfm_segments(data).copy()
    if rfm.empty:
        raise ValueError("At least one customer is required for segmentation.")

    cluster_count = min(n_clusters, len(rfm))
    features = ["recency_days", "frequency", "monetary"]
    scaled_features = StandardScaler().fit_transform(rfm[features])
    model = KMeans(n_clusters=cluster_count, random_state=42, n_init=20)
    rfm["cluster"] = model.fit_predict(scaled_features) + 1

    # Cluster ids are arbitrary. Rank groups on low recency, high frequency and
    # high monetary value to make their presentation stable and meaningful.
    profiles = rfm.groupby("cluster", as_index=False)[features].mean()
    profiles["value_score"] = (
        -profiles["recency_days"].rank(method="first")
        + profiles["frequency"].rank(method="first")
        + profiles["monetary"].rank(method="first")
    )
    ranked_clusters = profiles.sort_values("value_score", ascending=False)["cluster"].tolist()
    name_map = {cluster: CLUSTER_NAMES[index] for index, cluster in enumerate(ranked_clusters)}
    rfm["cluster_name"] = rfm["cluster"].map(name_map)
    return rfm.sort_values(["cluster_name", "monetary"], ascending=[True, False]).reset_index(drop=True)


def customer_cluster_summary(data: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    """Vat ML-segmenten samen tot aantallen en gemiddeld gedrag per groep."""
    clusters = cluster_customers(data, n_clusters=n_clusters)
    return (
        clusters.groupby(["cluster", "cluster_name"], as_index=False)
        .agg(
            customers=("customer_id", "nunique"),
            average_recency_days=("recency_days", "mean"),
            average_orders=("frequency", "mean"),
            revenue=("monetary", "sum"),
        )
        .sort_values("revenue", ascending=False)
        .reset_index(drop=True)
    )

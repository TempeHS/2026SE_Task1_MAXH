import pickle
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")  # non-interactive backend for Flask
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import os
import io
import base64

MODEL_PATH = os.path.join(os.path.dirname(__file__), "map_selection_model.sav")
DRAFT_DATA_PATH = os.path.join(os.path.dirname(__file__), "draft_phase.csv")


def load_model():
    with open(MODEL_PATH, "rb") as f:
        poly, final_model, alpha = pickle.load(f)
    return poly, final_model, alpha


def get_all_teams():
    df = pd.read_csv(DRAFT_DATA_PATH)
    teams = sorted(df["Team"].dropna().astype(str).str.strip().unique())
    return teams


def predict_maps(team_name: str):
    df = pd.read_csv(DRAFT_DATA_PATH)
    df = df.drop(columns=["Tournament", "Stage", "Match Type"])
    df["Team"] = df["Team"].astype(str).str.strip()
    df["Map"] = df["Map"].astype(str).str.strip()
    df["Action"] = df["Action"].astype(str).str.strip().str.lower()

    team_name_clean = team_name.strip().lower()

    # validate team exists
    all_teams_lower = df["Team"].str.lower().unique()
    if team_name_clean not in all_teams_lower:
        return None, None, f"Team '{team_name}' not found."

    # build teamdata
    team_rows = df[df["Team"].str.lower().eq(team_name_clean)].copy()
    teamdata = (
        pd.crosstab(team_rows["Map"], team_rows["Action"])
        .reindex(columns=["ban", "pick"], fill_value=0)
        .reset_index()
        .rename(columns={"Map": "map"})
        .sort_values("map")
        .reset_index(drop=True)
    )
    teamdata.insert(0, "team", team_rows["Team"].iloc[0])

    # build alldata (exclude chosen team)
    all_rows = df[~df["Team"].str.lower().eq(team_name_clean)].copy()
    all_rows = all_rows[all_rows["Action"].isin(["ban", "pick"])]
    alldata = (
        pd.crosstab(all_rows["Map"], all_rows["Action"])
        .reindex(columns=["ban", "pick"], fill_value=0)
        .reset_index()
        .rename(columns={"Map": "map"})
        .sort_values("map")
        .reset_index(drop=True)
    )

    for d in [alldata, teamdata]:
        d["map"] = d["map"].astype(str).str.strip()

    alldata["global_pick_rate"] = alldata["pick"] / alldata["pick"].sum()

    merged = alldata[["map", "global_pick_rate"]].merge(
        teamdata[["map", "team", "pick"]].rename(columns={"pick": "team_pick_actual"}),
        on="map",
        how="inner",
    )

    actual = merged["team_pick_actual"].to_numpy(dtype=float)
    actual_prob = actual / actual.sum() if actual.sum() > 0 else np.zeros_like(actual)
    merged["team_deviation"] = actual_prob - merged["global_pick_rate"].to_numpy()

    poly, final_model, alpha = load_model()

    X = merged[["global_pick_rate"]].to_numpy()
    X_poly = poly.transform(X)
    y_pred = final_model.predict(X_poly)
    y_pred_nonneg = np.clip(y_pred, 0, None)

    base_prob = (
        y_pred_nonneg / y_pred_nonneg.sum()
        if y_pred_nonneg.sum() > 0
        else np.repeat(1 / len(y_pred_nonneg), len(y_pred_nonneg))
    )

    pred_prob = base_prob + alpha * merged["team_deviation"].to_numpy()
    pred_prob = np.clip(pred_prob, 0, None)
    pred_prob = (
        pred_prob / pred_prob.sum()
        if pred_prob.sum() > 0
        else np.repeat(1 / len(pred_prob), len(pred_prob))
    )

    results = merged[["team", "map"]].copy()
    results["pick_probability"] = pred_prob
    results["actual_probability"] = actual_prob
    results = results.sort_values("pick_probability", ascending=False).reset_index(
        drop=True
    )

    # generate matplotlib chart as base64 string
    plot_df = results.copy()
    x = np.arange(len(plot_df))
    width = 0.4

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(
        x - width / 2,
        plot_df["actual_probability"],
        width=width,
        label="Actual probability",
        color="steelblue",
    )
    ax.bar(
        x + width / 2,
        plot_df["pick_probability"],
        width=width,
        label="Predicted probability",
        color="tomato",
    )
    ax.set_title(f"Map Pick Probabilities: {results['team'].iloc[0]}")
    ax.set_xlabel("Map")
    ax.set_ylabel("Probability")
    ax.set_xticks(x)
    ax.set_xticklabels(plot_df["map"], rotation=45, ha="right")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    chart_b64 = base64.b64encode(buf.read()).decode("utf-8")

    return results.to_dict(orient="records"), chart_b64, None

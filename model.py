# import mlcroissant as mlc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Datalist = mlc.Dataset add link to data set

df = pd.read_csv("draft_phase.csv")

# %% [markdown]
# ### Step 2: check the dataset

# %%
df.info()

# %% [markdown]
# Describe each column of data!!!

# %% [markdown]
# ### step 3: culling unnesacary data
#
# for my business problem there are multiple columns which either provide no impact to the indepedant variable, or complicate the matter with very little effect on the indepedant variable.
#
# thus we should cull them to get a much simpler and easier to design solution
#

# %% [markdown]
# ### the unnecassary data points are:
#
# tournament type:
# - this is unnecassary as it does not impact what maps are chosen, only where the teams play
#
# stage:
# - again only impacts where in the world the teams play
#
# match type:
# - only usefull to know what brackets the teams are in, and only impacts who vs's who
#
#

# %%
df = df.drop(columns=["Tournament", "Stage", "Match Type"])


# %% [markdown]
# We are then left with 4 columns:
#
# Match name:
# - this will be split along the "vs" to find what teams pick which maps against other teams

# %% [markdown]
# now we can find out how many unique teams there are
#

# %%
teams = sorted(df["Team"].dropna().unique())
print(f"unique teams: {len(teams)}")
print(teams)

# %% [markdown]
# and now we can find how many unique maps there are
#
# Sorts through maps dosent pick up NA values and finds all unique values

# %%
maps = sorted(df["Map"].dropna().unique())
print(f"unique maps: {len(maps)}")
print(maps)

# %% [markdown]
# Now we know that there are 48 teams with 11 different picks
#
# So lets now see how many times these teams amd maps appear

# %%
team_amount = df["Team"].value_counts()
map_amount = df["Map"].value_counts()
print(team_amount)
print(map_amount)

# %% [markdown]
# now lets see how many times each map is banned and picked

# %%
ban_counts = df.loc[df["Action"].eq("ban"), "Map"].value_counts()
print(f"banned {ban_counts}")

pick_counts = df.loc[df["Action"].eq("pick"), "Map"].value_counts()
print(f"picked {pick_counts}")

# %% [markdown]
# lets see this in a graph
#

# %%
map_action_counts = (
    pd.crosstab(df["Map"], df["Action"])
    .reindex(columns=["ban", "pick"], fill_value=0)
    .sort_index()
)

x = map_action_counts["pick"].to_numpy()
y = map_action_counts["ban"].to_numpy()

plt.figure(figsize=(8, 6))
plt.scatter(x, y, s=90, label="Maps")

# line of best fit
degree = 2
coeffs = np.polyfit(x, y, degree)
poly_fn = np.poly1d(coeffs)

x_fit = np.linspace(x.min(), x.max(), 200)
y_fit = poly_fn(x_fit)
plt.plot(x_fit, y_fit, color="red", linewidth=2, label=f"Best fit (deg {degree})")

# label each dot with map name
for map_name, row in map_action_counts.iterrows():
    plt.annotate(
        map_name,
        (row["pick"], row["ban"]),
        xytext=(5, 4),
        textcoords="offset points",
        fontsize=9,
    )

plt.xlabel("Picked Count")
plt.ylabel("Banned Count")
plt.title("Map Pick vs Ban Counts")
plt.grid(True, linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()

# %% [markdown]
# the graph pretty clearly shows a relationship where the more popular a map is to pick to more popular it is to ban, up to a point where the pick rate out weighs the want to ban the map

# %% [markdown]
# time to create new data, now that we have an overview of what our data looks like for everyteam, its time to look at what the individual pick/ban rates are for each team

# %%
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

df_plot = df.copy()
df_plot["Action"] = df_plot["Action"].str.lower().str.strip()

# Team + Map + Action frequency
freq = (
    df_plot.groupby(["Team", "Map", "Action"])
    .size()
    .reset_index(name="Frequency")
    .query("Action in ['ban', 'pick'] and Frequency > 0")
)

teams = sorted(freq["Team"].unique())
maps = sorted(freq["Map"].unique())

team_to_x = {team: i for i, team in enumerate(teams)}
map_to_y = {m: i for i, m in enumerate(maps)}

freq["x"] = freq["Team"].map(team_to_x)
freq["y"] = freq["Map"].map(map_to_y)
freq["z"] = freq["Frequency"]

# Find points that share exact same plotted coordinates
overlap_mask = freq.duplicated(subset=["x", "y", "z"], keep=False)

ban_only = freq[(freq["Action"] == "ban") & (~overlap_mask)]
pick_only = freq[(freq["Action"] == "pick") & (~overlap_mask)]
overlap = freq[overlap_mask]

fig = plt.figure(figsize=(22, 10))
ax = fig.add_subplot(111, projection="3d")

if not ban_only.empty:
    ax.scatter(
        ban_only["x"],
        ban_only["y"],
        ban_only["z"],
        c="tomato",
        s=45,
        alpha=0.9,
        label="Ban",
    )
if not pick_only.empty:
    ax.scatter(
        pick_only["x"],
        pick_only["y"],
        pick_only["z"],
        c="steelblue",
        s=45,
        alpha=0.9,
        label="Pick",
    )
if not overlap.empty:
    ax.scatter(
        overlap["x"],
        overlap["y"],
        overlap["z"],
        c="purple",
        s=55,
        alpha=0.95,
        label="Overlap (same x,y,z)",
    )

ax.set_xlabel("Teams")
ax.set_ylabel("Maps")
ax.set_zlabel("Frequency")
ax.set_title("3D Team-Map Frequency (Purple = overlapping points)")

ax.set_xticks(range(len(teams)))
ax.set_xticklabels(teams, rotation=90, fontsize=7)

ax.set_yticks(range(len(maps)))
ax.set_yticklabels(maps, fontsize=8)

ax.legend(loc="upper right")
plt.tight_layout()
plt.show()

# %% [markdown]
# this graph shows reasonbly clearly the more popular maps to ban as well as the ones to pick
#
# The following might be a bit clearer

# %%
df_plot = df.copy()
df_plot["Action"] = df_plot["Action"].str.lower().str.strip()

# Use both bans + picks together
team_map_height = (
    df_plot[df_plot["Action"].isin(["ban", "pick"])]
    .groupby(["Team", "Map"])
    .size()
    .unstack(fill_value=0)
    .sort_index()
)

teams = team_map_height.index.tolist()
maps = team_map_height.columns.tolist()

X, Y = np.meshgrid(np.arange(len(teams)), np.arange(len(maps)), indexing="ij")
Z = team_map_height.to_numpy()

fig = plt.figure(figsize=(20, 10))
ax = fig.add_subplot(111, projection="3d")

surf = ax.plot_surface(X, Y, Z, cmap="viridis", edgecolor="none", alpha=0.95)

ax.set_xlabel("Teams")
ax.set_ylabel("Maps")
ax.set_zlabel("Frequency")
ax.set_title("Team-Map Height Map (Ban + Pick Frequency)")

ax.set_xticks(np.arange(len(teams)))
ax.set_xticklabels(teams, rotation=90, fontsize=7)
ax.set_yticks(np.arange(len(maps)))
ax.set_yticklabels(maps, fontsize=8)

fig.colorbar(surf, ax=ax, pad=0.1, shrink=0.6, label="Frequency")
plt.tight_layout()
plt.show()

# %% [markdown]
# now since we have a thorough idea of the data it is time to start trying to predict

# %% [markdown]
# The below code asksfor a team then shows every game of who they played
# !clean up so it only shows team a for action a

# %%
What_team = input("what team: ").strip().lower()

split_teams = (
    df["Match Name"]
    .str.split(r"\s+vs\s+", n=1, expand=True)
    .apply(lambda s: s.str.strip())
)

left = split_teams[0]
right = split_teams[1]
left_key = left.str.lower()
right_key = right.str.lower()

# keep rows where the match includes the chosen team
involved = left_key.eq(What_team) | right_key.eq(What_team)

results = df.loc[involved, ["Match Name", "Team", "Action", "Map"]].copy()

# force Team A = chosen team, Team B = opponent
results["Team A"] = np.where(
    left_key[involved].eq(What_team), left[involved], right[involved]
)
results["Team B"] = np.where(
    left_key[involved].eq(What_team), right[involved], left[involved]
)

# mark which side made the action
team_key = results["Team"].str.strip().str.lower()
team_a_key = results["Team A"].str.strip().str.lower()
results["Side"] = np.where(team_key.eq(team_a_key), "A", "B")

# combine action + map
results["Action Map"] = (
    results["Action"].astype(str).str.strip()
    + " "
    + results["Map"].astype(str).str.strip()
)

# pair Team A and Team B actions side-by-side per match
results["Turn"] = results.groupby(["Match Name", "Side"]).cumcount()

formatted = (
    results.pivot_table(
        index=["Match Name", "Team A", "Team B", "Turn"],
        columns="Side",
        values="Action Map",
        aggfunc="first",
    )
    .rename(columns={"A": "Team A Action Map", "B": "Team B Action Map"})
    .reset_index()
    .drop(columns="Turn")
    .fillna("")
)

formatted = formatted[
    ["Match Name", "Team A", "Team A Action Map", "Team B", "Team B Action Map"]
]

print(formatted.to_string(index=False))

# %% [markdown]
# now we need to take only team A and team B

# %%
team_a = input("team A").strip().lower()
team_b = input("Team b").strip().lower()

split_teams = (
    df["Match Name"]
    .str.split(r"\s+vs\s+", n=1, expand=True)
    .apply(lambda s: s.str.strip())
)

left = split_teams[0]
right = split_teams[1]
left_key = left.str.lower()
right_key = right.str.lower()

teamcombo_mask = (left_key.eq(team_a) & right_key.eq(team_b)) | (
    left_key.eq(team_b) & right_key.eq(team_a)
)

team_combo = df.loc[teamcombo_mask, ["Match Name", "Team", "Action", "Map"]].copy()
team_combo["team_key"] = team_combo["Team"].str.strip().str.lower()

team_a_only = team_combo[team_combo["team_key"].eq(team_a)].copy()

if team_a_only.empty:
    print("No rows found for that Team A vs Team B matchup.")
else:
    team_a_only["Action"] = team_a_only["Action"].astype(str).str.strip().str.lower()
    team_a_only["Map"] = team_a_only["Map"].astype(str).str.strip()
    print(team_a_only[["Match Name", "Team", "Action", "Map"]].to_string(index=False))

# %% [markdown]
# lets see what the most popular maps for each team is now

# %%
team_name = input("what team do you want to predict ").strip().lower()

team_rows = df[df["Team"].astype(str).str.strip().str.lower().eq(team_name)].copy()

if team_rows.empty:
    print("No rows found for that team.")
else:
    team_rows["Action"] = team_rows["Action"].astype(str).str.strip().str.lower()
    team_rows["Map"] = team_rows["Map"].astype(str).str.strip()

    map_action_counts = (
        pd.crosstab(team_rows["Map"], team_rows["Action"])
        .reindex(columns=["ban", "pick"], fill_value=0)
        .sort_index()
    )

    ax = map_action_counts.plot(
        kind="bar",
        figsize=(12, 6),
        width=0.8,
        color=["tomato", "steelblue"],
    )
    ax.set_title(f"Bans and Picks by Map for: {team_rows['Team'].iloc[0]}")
    ax.set_xlabel("Map")
    ax.set_ylabel("Count")
    ax.legend(["Ban", "Pick"])
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


team_rows = df[df["Team"].astype(str).str.strip().str.lower().eq(team_name)].copy()

if team_rows.empty:
    print("No rows found for that team.")
    teamdata = pd.DataFrame(columns=["team", "map", "ban", "pick"])
else:
    team_rows["Action"] = team_rows["Action"].astype(str).str.strip().str.lower()
    team_rows["Map"] = team_rows["Map"].astype(str).str.strip()

    # one row per map with number of bans by this team
    teamdata = (
        pd.crosstab(team_rows["Map"], team_rows["Action"])
        .reindex(columns=["ban", "pick"], fill_value=0)
        .reset_index()
        .rename(columns={"Map": "map"})
        .sort_values("map")
        .reset_index(drop=True)
    )

    teamdata.insert(0, "team", team_rows["Team"].iloc[0])

print(teamdata)
if not teamdata.empty:
    safe_team = team_name.replace(" ", "_")
    output_path = Path.cwd() / f"teamdata_{safe_team}.csv"
    teamdata.to_csv("teamdata.csv", index=False)
    print(f"Saved: {output_path}")
else:
    print("teamdata is empty, not saving.")

if "team_name" not in locals():
    raise NameError("Run cell 36 first so 'team_name' is defined.")

excluded_team = str(team_name).strip().lower()

all_rows = df.copy()
all_rows["Team"] = all_rows["Team"].astype(str).str.strip()
all_rows["Map"] = all_rows["Map"].astype(str).str.strip()
all_rows["Action"] = all_rows["Action"].astype(str).str.strip().str.lower()

# remove the chosen team from cell 36
all_rows = all_rows[~all_rows["Team"].str.lower().eq(excluded_team)].copy()

# keep only ban/pick actions
all_rows = all_rows[all_rows["Action"].isin(["ban", "pick"])].copy()

# counts per map from remaining teams
mapdata = (
    pd.crosstab(all_rows["Map"], all_rows["Action"])
    .reindex(columns=["ban", "pick"], fill_value=0)
    .reset_index()
    .rename(columns={"Map": "map"})
    .sort_values("map")
    .reset_index(drop=True)
)

print(f"Excluded team: {team_name}")
print(mapdata)

output_path = Path.cwd() / "alldata.csv"
mapdata.to_csv(output_path, index=False)
print(f"Saved: {output_path}")

# %% [markdown]
# no we can combine them into a compelte data table for specfic teams

# %%
# Load both datasets
all_df = pd.read_csv("alldata.csv")
team_df = pd.read_csv("teamdata.csv")

# Clean keys
all_df["map"] = all_df["map"].astype(str).str.strip()
team_df["map"] = team_df["map"].astype(str).str.strip()

# Ensure numeric
for col in ["ban", "pick"]:
    all_df[col] = pd.to_numeric(all_df[col], errors="coerce").fillna(0)
    team_df[col] = pd.to_numeric(team_df[col], errors="coerce").fillna(0)

# Preview both datasets to confirm they are ready for model.ipynb
print("=== alldata.csv (all teams except chosen) ===")
print(all_df.to_string(index=False))

print("\n=== teamdata.csv (chosen team only) ===")
print(team_df.to_string(index=False))

print("\nReady for model.ipynb — specific.csv is no longer needed.")
print(f"Total team picks: {int(team_df['pick'].sum())}")
print(f"Total global picks: {int(all_df['pick'].sum())}")


# %%
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import LeaveOneOut
import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# Load datasets (generated by development.ipynb)
alldata = pd.read_csv("alldata.csv")  # all teams EXCEPT chosen team
teamdata = pd.read_csv("teamdata.csv")  # chosen team only

# Clean keys
for d in [alldata, teamdata]:
    d["map"] = d["map"].astype(str).str.strip()

# Global pick rate from all other teams
alldata["global_pick_rate"] = alldata["pick"] / alldata["pick"].sum()

# Merge global rate into team data
merged = alldata[["map", "global_pick_rate"]].merge(
    teamdata[["map", "team", "pick"]].rename(columns={"pick": "team_pick_actual"}),
    on="map",
    how="inner",
)

actual = merged["team_pick_actual"].to_numpy(dtype=float)
actual_prob = actual / actual.sum() if actual.sum() > 0 else np.zeros_like(actual)


merged["team_deviation"] = actual_prob - merged["global_pick_rate"].to_numpy()


X = merged[["global_pick_rate"]].to_numpy()
y = merged["team_pick_actual"].to_numpy(dtype=float)

loo = LeaveOneOut()
loo_preds = np.zeros_like(y)
poly = PolynomialFeatures(degree=2)

for train_idx, test_idx in loo.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train = y[train_idx]

    X_train_poly = poly.fit_transform(X_train)
    X_test_poly = poly.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_poly, y_train)

    loo_preds[test_idx] = np.clip(model.predict(X_test_poly), 0, None)

r2_loo = r2_score(y, loo_preds)
print(f"LOO cross-validated R² (count space): {r2_loo:.4f}")

# Final model trained on ALL data
X_poly_all = poly.fit_transform(X)
final_model = LinearRegression()
final_model.fit(X_poly_all, y)

y_pred = final_model.predict(X_poly_all)
y_pred_nonneg = np.clip(y_pred, 0, None)

# Normalize model output to probabilities
base_prob = (
    y_pred_nonneg / y_pred_nonneg.sum()
    if y_pred_nonneg.sum() > 0
    else np.repeat(1 / len(y_pred_nonneg), len(y_pred_nonneg))
)

# alpha controls how much team history shifts the prediction
alpha = 0.9
pred_prob = base_prob + alpha * merged["team_deviation"].to_numpy()

# Clip and renormalize (deviation adjustment can push values negative)
pred_prob = np.clip(pred_prob, 0, None)
pred_prob = (
    pred_prob / pred_prob.sum()
    if pred_prob.sum() > 0
    else np.repeat(1 / len(pred_prob), len(pred_prob))
)

r2_prob = r2_score(actual_prob, pred_prob)
print(f"Train R² (probability space): {r2_prob:.4f}")

# Build results table
results = merged[["team", "map", "team_pick_actual"]].copy()
results["predicted_picks"] = y_pred_nonneg
results["pick_probability"] = pred_prob
results["actual_probability"] = actual_prob

print("\nMap Selection Probabilities:")
print(results.to_string(index=False))

best_row = results.loc[results["pick_probability"].idxmax()]
worst_row = results.loc[results["pick_probability"].idxmin()]
print(
    f"\nBest probability map:   {best_row['map']} ({best_row['pick_probability']:.2%})"
)
print(
    f"Lowest probability map: {worst_row['map']} ({worst_row['pick_probability']:.2%})"
)

# Save model
filename = "map_selection_model.sav"
pickle.dump((poly, final_model, alpha), open(filename, "wb"))
print(f"\nModel saved as: {filename}")

# Plot actual vs predicted probabilities
plot_df = results.sort_values("pick_probability", ascending=False).reset_index(
    drop=True
)
x = np.arange(len(plot_df))
width = 0.4

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(
    x - width / 2,
    plot_df["actual_probability"],
    width=width,
    label="Actual probability",
)
ax.bar(
    x + width / 2,
    plot_df["pick_probability"],
    width=width,
    label="Predicted probability",
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
plt.show()

# %% [markdown]
# now to export this

# %%
filename = "map_selection_model.sav"
pickle.dump((poly, final_model, alpha), open(filename, "wb"))

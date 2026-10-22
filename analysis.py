from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# File locations
project_dir = Path(__file__).resolve().parent
csv_path = project_dir / "data" / "player_stats.csv"
output_dir = project_dir / "outputs"
output_dir.mkdir(exist_ok=True)

# Read the CSV. NA and blank cells remain missing values.
df = pd.read_csv(csv_path)

print("\nPLAYER DATA")
print(df.to_string(index=False))

print("\nMISSING VALUES")
print(df.isna().sum())

print(f"\nPlayers: {len(df)}")
print(f"Columns: {len(df.columns)}")

# Check the values needed for the passing chart.
passing_columns = [
    "minutes_played",
    "passes_attempted",
    "accurate_passes",
]

if df[passing_columns].isna().any().any():
    raise ValueError("Minutes or passing counts are missing. Check the CSV.")

if (df["passes_attempted"] < 0).any():
    raise ValueError("Pass attempts cannot be negative.")

if (
    (df["accurate_passes"] < 0)
    | (df["accurate_passes"] > df["passes_attempted"])
).any():
    raise ValueError("Completed passes must be between zero and attempts.")

# Calculate percentages. No attempts means an undefined percentage.
df["shot_accuracy_pct"] = (
    df["shots_on_target"]
    .div(df["shots"].replace(0, float("nan")))
    .mul(100)
    .round(2)
)

df["dribble_success_pct"] = (
    df["dribbles_completed"]
    .div(df["dribbles_attempted"].replace(0, float("nan")))
    .mul(100)
    .round(2)
)

df["pass_accuracy_pct"] = (
    df["accurate_passes"]
    .div(df["passes_attempted"].replace(0, float("nan")))
    .mul(100)
    .round(2)
)

comparison_columns = [
    "player",
    "minutes_played",
    "goals",
    "assists",
    "shot_accuracy_pct",
    "dribble_success_pct",
    "pass_accuracy_pct",
    "tackles_won",
    "interceptions",
]

print("\nPLAYER COMPARISON")
print(
    df[comparison_columns].to_string(
        index=False,
        na_rep="N/A",
    )
)

# Passing chart
labels = (
    df["player"]
    + " ("
    + df["minutes_played"].astype(int).astype(str)
    + " min)"
)

completed = df["accurate_passes"]
unsuccessful = df["passes_attempted"] - completed
positions = list(range(len(df)))

fig, ax = plt.subplots(figsize=(11, 5.5))

ax.barh(
    positions,
    completed,
    label="Completed",
    color="#2563eb",
)

ax.barh(
    positions,
    unsuccessful,
    left=completed,
    label="Unsuccessful",
    color="#cbd5e1",
)

ax.set_yticks(positions)
ax.set_yticklabels(labels)

for i, row in df.reset_index(drop=True).iterrows():
    accuracy = row["pass_accuracy_pct"]
    accuracy_label = (
        f"{accuracy:.1f}%" if pd.notna(accuracy) else "N/A"
    )

    ax.text(
        row["passes_attempted"] + 0.5,
        i,
        f'{int(row["accurate_passes"])}/'
        f'{int(row["passes_attempted"])} '
        f"({accuracy_label})",
        va="center",
        fontsize=9,
    )

ax.set_xlim(0, max(df["passes_attempted"].max() * 1.4, 10))
ax.invert_yaxis()
ax.set_xlabel("Passes")
ax.set_title(
    "Passing comparison | Elche vs Barcelona | 23 August 2026"
)
ax.legend()
ax.spines[["top", "right"]].set_visible(False)

fig.text(
    0.01,
    0.01,
    "Source: Footballen | Selected players; playing time differs. "
    "Data provisional.",
    fontsize=8,
    color="#555555",
)

fig.tight_layout(rect=[0, 0.05, 1, 1])

chart_path = output_dir / "passing_comparison.png"
fig.savefig(chart_path, dpi=200)
plt.close(fig)

print(f"\nSaved chart: {chart_path}")

# Compare defensive actions without treating missing values as zero.
defensive_metrics = {
    "tackles_won": "Tackles won",
    "interceptions": "Interceptions",
    "clearances": "Clearances",
}

fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)

for ax, (column, title) in zip(axes, defensive_metrics.items()):
    values = df[column]

    for i, value in enumerate(values):
        if pd.isna(value):
            ax.text(0.1, i, "N/A", va="center", color="#777777")
        else:
            ax.barh(i, value, color="#2563eb")
            ax.text(value + 0.1, i, f"{value:g}", va="center")

    maximum = values.max()
    ax.set_xlim(0, max(maximum + 1, 2) if pd.notna(maximum) else 2)
    ax.set_title(title)
    ax.set_xlabel("Actions")
    ax.set_yticks(positions)
    ax.set_yticklabels(labels)
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.spines[["top", "right"]].set_visible(False)

axes[0].invert_yaxis()

fig.suptitle(
    "Defensive actions | Elche vs Barcelona | 23 August 2026"
)

fig.text(
    0.01,
    0.01,
    "Sources: CSV source links | Data provisional. "
    "N/A means unavailable. Roles and playing time differ.",
    fontsize=8,
    color="#555555",
)

fig.tight_layout(rect=[0, 0.06, 1, 0.94])

chart_path = output_dir / "defensive_comparison.png"
fig.savefig(chart_path, dpi=200)
plt.close(fig)

print(f"Saved chart: {chart_path}")

# Attacking contributions: show goals and assists separately.
fig, ax = plt.subplots(figsize=(11, 5.5))
bar_height = 0.35

ax.barh(
    [i - bar_height / 2 for i in positions],
    df["goals"],
    height=bar_height,
    label="Goals",
    color="#2563eb",
)

ax.barh(
    [i + bar_height / 2 for i in positions],
    df["assists"],
    height=bar_height,
    label="Assists",
    color="#f59e0b",
)

for i, row in df.reset_index(drop=True).iterrows():
    ax.text(
        row["goals"] + 0.05,
        i - bar_height / 2,
        str(int(row["goals"])),
        va="center",
    )
    ax.text(
        row["assists"] + 0.05,
        i + bar_height / 2,
        str(int(row["assists"])),
        va="center",
    )

ax.set_yticks(positions)
ax.set_yticklabels(labels)
ax.invert_yaxis()
ax.set_xlim(0, max(df["goals"].max(), df["assists"].max()) + 1)
ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
ax.set_xlabel("Count")
ax.set_title(
    "Goals and assists | Elche vs Barcelona | 23 August 2026"
)
ax.legend()
ax.spines[["top", "right"]].set_visible(False)

fig.text(
    0.01,
    0.01,
    "Sources: CSV source links | Data provisional. "
    "Selected players; roles and playing time differ.",
    fontsize=8,
    color="#555555",
)

fig.tight_layout(rect=[0, 0.05, 1, 1])

chart_path = output_dir / "attacking_comparison.png"
fig.savefig(chart_path, dpi=200)
plt.close(fig)

print(f"Saved chart: {chart_path}")

# Display all three saved charts side by side in one window.
chart_files = [
    "passing_comparison.png",
    "defensive_comparison.png",
    "attacking_comparison.png",
]

fig, axes = plt.subplots(1, 3, figsize=(20, 7))
fig.canvas.manager.set_window_title("Barcelona vs Elche — Player Analysis")

for ax, filename in zip(axes, chart_files):
    image = plt.imread(output_dir / filename)
    ax.imshow(image)
    ax.axis("off")

fig.tight_layout(pad=0.5)
plt.show()
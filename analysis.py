"""
Germany Solar PV Market Analysis
---------------------------------
Reproduces the key charts from the Excel dashboard using pandas + matplotlib,
and prints the market-intelligence findings used to prioritize IP67 solar
enclosure export sales into the German market.

Data sources: Bundesnetzagentur (German Federal Network Agency) and
Fraunhofer ISE (energy-charts.info). See README.md for full citations.

Run:  python3 analysis.py
Outputs: PNG charts in ./charts/, key findings printed to stdout.
"""
import pandas as pd
import matplotlib.pyplot as plt
import os

DATA_DIR = "data"
CHART_DIR = "charts"
os.makedirs(CHART_DIR, exist_ok=True)

plt.rcParams["font.family"] = "DejaVu Sans"
NAVY, BLUE, ORANGE, LIGHT_BLUE = "#1F3864", "#2E75B6", "#ED7D31", "#9DC3E6"


def load_data():
    national = pd.read_csv(f"{DATA_DIR}/national_annual.csv")
    states = pd.read_csv(f"{DATA_DIR}/state_data_2025.csv")
    segments = pd.read_csv(f"{DATA_DIR}/segment_data.csv")
    return national, states, segments


def chart_cumulative_capacity(national):
    df = national.dropna(subset=["cumulative_installed_gw"])
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(df["year"], df["cumulative_installed_gw"], marker="o", color=NAVY, linewidth=2.5)
    ax.set_title("Germany — Cumulative Installed Solar PV Capacity (GW)", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_xlabel("Year")
    ax.set_ylabel("GW")
    ax.grid(axis="y", alpha=0.3)
    for x, y in zip(df["year"], df["cumulative_installed_gw"]):
        ax.annotate(f"{y:.0f}", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(f"{CHART_DIR}/01_cumulative_capacity.png", dpi=150)
    plt.close(fig)


def chart_annual_additions(national):
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [BLUE if str(c).startswith("Confirmed") else "#B7C9DE" for c in national["data_confidence"]]
    ax.bar(national["year"].astype(str), national["annual_addition_gw"], color=colors)
    ax.set_title("Germany — Annual Net Solar PV Additions (GW)", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_xlabel("Year")
    ax.set_ylabel("GW added")
    ax.axhline(22, color=ORANGE, linestyle="--", linewidth=1.5, label="2026 target: 22 GW/yr (215 GW by 2030)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"{CHART_DIR}/02_annual_additions.png", dpi=150)
    plt.close(fig)


def chart_top_states(states):
    df = states[states["rank_2025"].notna()].sort_values("addition_2025_mw", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(df["state"], df["addition_2025_mw"], color=ORANGE)
    ax.set_title("2025 Net Solar Additions by German State (MW)", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_xlabel("MW added in 2025")
    for y, (val) in enumerate(df["addition_2025_mw"]):
        ax.text(val + 30, y, f"{val:,.0f}", va="center", fontsize=9)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"{CHART_DIR}/03_top_states_2025.png", dpi=150)
    plt.close(fig)


def chart_segment_split(segments):
    fig, ax = plt.subplots(figsize=(9, 5))
    x = segments["period"]
    ax.bar(x, segments["ground_mount_mw"], label="Ground-mount / utility-scale", color=NAVY)
    ax.bar(x, segments["rooftop_building_mw"], bottom=segments["ground_mount_mw"],
           label="Rooftop / building-mounted", color=LIGHT_BLUE)
    ax.set_title("Ground-mount vs Rooftop Additions (MW)\nIP67 Enclosure Demand Signal", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_ylabel("MW")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"{CHART_DIR}/04_segment_split.png", dpi=150)
    plt.close(fig)


def print_findings(national, states, segments):
    latest = national[national["year"] == 2025].iloc[0]
    mid2026 = national[national["year"] == 2026].iloc[0]
    bavaria = states.iloc[0]
    total_2025_state = states["addition_2025_mw"].sum()
    seg_2025 = segments[segments["period"] == "2025 (full year)"].iloc[0]
    seg_h1_2026 = segments[segments["period"] == "H1 2026"].iloc[0]

    print("\n=== KEY FINDINGS ===")
    print(f"1. Installed capacity reached {latest['cumulative_installed_gw']:.0f} GW at end of 2025, "
          f"growing to {mid2026['cumulative_installed_gw']:.1f} GW by mid-2026.")
    print(f"2. Germany added {latest['annual_addition_gw']:.1f} GW in 2025 — but needs ~22 GW/year "
          f"to hit its 215 GW-by-2030 target, a ~34% acceleration from 2025's pace.")
    print(f"3. {bavaria['state']} led all states with {bavaria['addition_2025_mw']:,.0f} MW added in 2025 "
          f"({bavaria['addition_2025_mw']/total_2025_state:.1%} of the national total) — "
          f"the top 3 states (Bavaria, Baden-Württemberg, NRW) account for "
          f"{states.iloc[0:3]['addition_2025_mw'].sum()/total_2025_state:.1%} of all state-attributed additions.")
    print(f"4. Ground-mount/utility-scale installations — the segment needing the most heavy-duty IP67 "
          f"enclosures — made up {seg_2025['ground_mount_share']:.1%} of 2025 additions and "
          f"{seg_h1_2026['ground_mount_share']:.1%} of H1 2026 additions, a rising share.")
    print("====================\n")


if __name__ == "__main__":
    national, states, segments = load_data()
    chart_cumulative_capacity(national)
    chart_annual_additions(national)
    chart_top_states(states)
    chart_segment_split(segments)
    print_findings(national, states, segments)
    print(f"Charts saved to ./{CHART_DIR}/")

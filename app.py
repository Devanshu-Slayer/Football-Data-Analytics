# -*- coding: utf-8 -*-
"""
Football Player Performance Analytics Dashboard
================================================
Synthetic data -- not real-world football statistics.
Built with Python, Streamlit, Pandas, Plotly
"""

import os
import io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ──────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────
CSV_PATH = "football_players.csv"

TEAMS = ["United FC", "City FC", "Arsenal FC", "Chelsea FC", "Liverpool FC", "Spurs FC"]
POSITIONS = ["GK", "DEF", "MID", "FWD"]
SEASONS = ["2021-22", "2022-23", "2023-24"]
NATIONALITIES = [
    "England", "Brazil", "France", "Spain", "Germany",
    "Portugal", "Argentina", "Netherlands", "Italy", "Belgium",
    "Nigeria", "Senegal", "Japan", "Uruguay", "Colombia",
]

FIRST_NAMES = [
    "James", "Luca", "Marco", "Carlos", "Antoine", "Sergio", "Kai",
    "Trent", "Mason", "Phil", "Bukayo", "Erling", "Vinicius", "Pedri",
    "Declan", "Jude", "Rodri", "Gavi", "Kylian", "Leandro", "Rafinha",
    "Bruno", "Ruben", "Diogo", "Darwin", "Dominic", "Ivan", "Richarlison",
    "Gabriel", "Ben", "Reece", "Conor", "Marcus", "Jadon", "Harry",
    "Son", "Pierre", "Romelu", "Tammy", "Timo", "Christian", "Hakim",
    "Thiago", "Jordan", "Fabinho", "Alisson", "Ederson", "David", "Hugo",
    "Kyle", "Joao", "Bernardo", "Kevin", "Ilkay", "Riyad", "Jack",
]

LAST_NAMES = [
    "Smith", "Silva", "Martinez", "Hernandez", "Muller", "Fernandez", "Havertz",
    "Alexander-Arnold", "Mount", "Foden", "Saka", "Haaland", "Junior", "Garcia",
    "Rice", "Bellingham", "Rodrigo", "Gomes", "Mbappe", "Telles", "Coutinho",
    "Fernandes", "Dias", "Jota", "Nunez", "Calvert-Lewin", "Perisic", "Richarlison",
    "Jesus", "White", "James", "Gallagher", "Rashford", "Sancho", "Kane",
    "Heung-min", "Emile-Smith Rowe", "Lukaku", "Abraham", "Werner", "Pulisic", "Ziyech",
    "Alcantara", "Henderson", "Fabinho", "Becker", "De Gea", "Ospina", "Lloris",
    "Walker", "Cancelo", "Silva", "De Bruyne", "Gundogan", "Mahrez", "Grealish",
]

# Pitch-green Plotly colour sequence
GREEN_PALETTE = [
    "#00c853", "#1de9b6", "#64dd17", "#aeea00",
    "#ffab00", "#ff6d00", "#dd2c00", "#6200ea",
    "#304ffe", "#0091ea", "#00b8d4", "#00bfa5",
]

PLOTLY_TEMPLATE = "plotly_dark"
ACCENT = "#00c853"


# ──────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ──────────────────────────────────────────────────
st.set_page_config(
    page_title="⚽ Football Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ──────────────────────────────────────────────────
# GLOBAL CSS — dark football pitch theme
# ──────────────────────────────────────────────────
def inject_css() -> None:
    st.markdown(
        """
        <style>
        /* ── Main background ── */
        .stApp { background-color: #0e1117; }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background-color: #1a1f2e;
            border-right: 1px solid #2a2f3e;
        }

        /* ── Hide default Streamlit header/footer ── */
        #MainMenu, footer, header { visibility: hidden; }

        /* ── KPI card row ── */
        .kpi-row {
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            margin-bottom: 24px;
        }
        .kpi-card {
            flex: 1;
            min-width: 140px;
            background: #1e2536;
            border: 1px solid #2a3550;
            border-top: 3px solid #00c853;
            border-radius: 8px;
            padding: 16px 18px 14px;
        }
        .kpi-label {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: #8899aa;
            margin-bottom: 6px;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: 800;
            color: #00c853;
            line-height: 1.1;
        }
        .kpi-sub {
            font-size: 12px;
            color: #57606a;
            margin-top: 4px;
        }

        /* ── Section header ── */
        .section-header {
            font-size: 18px;
            font-weight: 700;
            color: #e6edf3;
            border-left: 4px solid #00c853;
            padding-left: 10px;
            margin: 20px 0 14px;
        }

        /* ── Synthetic data banner ── */
        .synthetic-banner {
            background: #1a2a1a;
            border: 1px solid #00c853;
            border-radius: 6px;
            padding: 10px 16px;
            color: #00c853;
            font-size: 13px;
            margin-bottom: 20px;
        }

        /* ── Dataframe ── */
        [data-testid="stDataFrame"] { border-radius: 6px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────
# DATA GENERATION
# ──────────────────────────────────────────────────
def generate_data() -> pd.DataFrame:
    """
    Generate a reproducible synthetic football player dataset.
    120 players × 3 seasons = 360 rows.
    Seeded at 42 for full reproducibility.
    """
    rng = np.random.default_rng(42)

    # Position slots per team: 2 GK, 5 DEF, 5 MID, 3 FWD = 15 players per team
    pos_slots = ["GK"] * 2 + ["DEF"] * 5 + ["MID"] * 5 + ["FWD"] * 3
    records = []
    player_id = 1

    # Build per-player fixed attributes
    players = []
    fn_pool = FIRST_NAMES.copy()
    ln_pool = LAST_NAMES.copy()
    rng.shuffle(fn_pool)
    rng.shuffle(ln_pool)
    name_idx = 0

    for team in TEAMS:
        for pos in pos_slots:
            fn = fn_pool[name_idx % len(fn_pool)]
            ln = ln_pool[name_idx % len(ln_pool)]
            players.append(
                {
                    "player_id": player_id,
                    "player_name": f"{fn} {ln}",
                    "team": team,
                    "position": pos,
                    "age": int(np.clip(float(rng.normal(26, 4)), 17, 35)),
                    "nationality": NATIONALITIES[
                        int(rng.choice(len(NATIONALITIES), p=[
                            0.15, 0.12, 0.10, 0.09, 0.08,
                            0.07, 0.07, 0.06, 0.06, 0.05,
                            0.04, 0.04, 0.03, 0.02, 0.02,
                        ]))
                    ],
                }
            )
            player_id += 1
            name_idx += 1

    # Per-season performance — position-weighted stats
    goal_max   = {"GK": 1,  "DEF": 5,  "MID": 12, "FWD": 25}
    assist_max = {"GK": 2,  "DEF": 6,  "MID": 15, "FWD": 10}
    tackle_max = {"GK": 2,  "DEF": 80, "MID": 50, "FWD": 20}
    pass_base  = {"GK": 30, "DEF": 45, "MID": 60, "FWD": 35}
    pass_acc   = {"GK": 72, "DEF": 78, "MID": 83, "FWD": 75}

    for p in players:
        pos = p["position"]
        for season in SEASONS:
            appearances = int(rng.integers(5, 38))
            minutes = int(min(appearances * int(np.clip(float(rng.normal(76, 8)), 50, 90)), 3420))
            goals   = int(rng.integers(0, goal_max[pos] + 1))
            assists = int(rng.integers(0, assist_max[pos] + 1))
            shots   = int(max(goals * int(rng.uniform(2, 5)) + int(rng.integers(0, 5)), goals))
            sot     = int(min(max(int(shots * rng.uniform(0.35, 0.55)), goals), shots))
            passes  = int(appearances * int(np.clip(float(rng.normal(pass_base[pos], 8)), 10, 90)))
            p_acc   = round(float(np.clip(float(rng.normal(pass_acc[pos], 5)), 55, 97)), 1)
            tackles = int(rng.integers(0, tackle_max[pos] + 1))
            yellows = int(rng.integers(0, 9))
            reds    = int(rng.integers(0, 3))
            cs      = int(rng.integers(0, 21)) if pos in ("GK", "DEF") else 0

            # Composite rating: weighted blend of normalised stats
            goal_score   = min(goals / max(goal_max[pos], 1), 1.0)
            assist_score = min(assists / max(assist_max[pos], 1), 1.0)
            acc_score    = (p_acc - 55) / 42  # normalise 55–97 → 0–1
            discipline   = 1 - (yellows * 0.03 + reds * 0.10)
            raw_rating   = (
                goal_score * 0.30
                + assist_score * 0.25
                + acc_score * 0.25
                + discipline * 0.20
            )
            rating = round(float(6.0 + raw_rating * 3.5 + np.clip(float(rng.normal(0, 0.2)), -0.5, 0.5)), 2)
            rating = round(float(np.clip(rating, 6.0, 9.5)), 2)

            records.append(
                {
                    **p,
                    "season": season,
                    "appearances": appearances,
                    "minutes_played": minutes,
                    "goals": goals,
                    "assists": assists,
                    "shots": shots,
                    "shots_on_target": sot,
                    "passes": passes,
                    "pass_accuracy": p_acc,
                    "tackles": tackles,
                    "yellow_cards": yellows,
                    "red_cards": reds,
                    "clean_sheets": cs,
                    "rating": rating,
                }
            )

    df = pd.DataFrame(records)
    df.to_csv(CSV_PATH, index=False)
    return df


# ──────────────────────────────────────────────────
# DATA LOADING
# ──────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading player data…")
def load_data() -> pd.DataFrame:
    if not os.path.exists(CSV_PATH):
        generate_data()

    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as exc:
        st.error(
            f"❌ Could not read '{CSV_PATH}': {exc}\n\n"
            "Ensure the file exists in the same folder as app.py, then refresh."
        )
        st.stop()

    # Type safety
    int_cols = [
        "player_id", "age", "appearances", "minutes_played",
        "goals", "assists", "shots", "shots_on_target",
        "passes", "tackles", "yellow_cards", "red_cards", "clean_sheets",
    ]
    float_cols = ["pass_accuracy", "rating"]
    for c in int_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    for c in float_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Fill remaining NaNs with sensible defaults
    df["rating"] = df["rating"].fillna(df["rating"].median())
    df["pass_accuracy"] = df["pass_accuracy"].fillna(df["pass_accuracy"].median())

    return df


# ──────────────────────────────────────────────────
# SIDEBAR FILTERS
# ──────────────────────────────────────────────────
def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown(
        "<div style='text-align:center;padding:10px 0 4px;font-size:28px;'>⚽</div>"
        "<div style='text-align:center;font-size:15px;font-weight:700;"
        "color:#00c853;margin-bottom:18px;'>Football Analytics</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("### 🔍 Filters")

    all_seasons  = sorted(df["season"].unique().tolist())
    all_teams    = sorted(df["team"].unique().tolist())
    all_positions = ["GK", "DEF", "MID", "FWD"]

    seasons = st.sidebar.multiselect(
        "Season", all_seasons, default=all_seasons, key="filter_season"
    )
    teams = st.sidebar.multiselect(
        "Team", all_teams, default=all_teams, key="filter_team"
    )
    positions = st.sidebar.multiselect(
        "Position", all_positions, default=all_positions, key="filter_position"
    )
    name_search = st.sidebar.text_input("🔎 Player Name Search", key="filter_name")
    min_apps = st.sidebar.slider(
        "Min. Appearances", min_value=1, max_value=38, value=1, key="filter_apps"
    )

    return apply_filters(df, seasons, teams, positions, name_search, min_apps)


def apply_filters(
    df: pd.DataFrame,
    seasons: list,
    teams: list,
    positions: list,
    name_search: str,
    min_apps: int,
) -> pd.DataFrame:
    if seasons:
        df = df[df["season"].isin(seasons)]
    if teams:
        df = df[df["team"].isin(teams)]
    if positions:
        df = df[df["position"].isin(positions)]
    if name_search.strip():
        df = df[df["player_name"].str.contains(name_search.strip(), case=False, na=False)]
    df = df[df["appearances"] >= min_apps]
    return df


# ──────────────────────────────────────────────────
# KPI CARDS
# ──────────────────────────────────────────────────
def render_kpi_cards(df: pd.DataFrame) -> None:
    total_players   = df["player_id"].nunique()
    total_goals     = int(df["goals"].sum())
    total_assists   = int(df["assists"].sum())
    total_minutes   = int(df["minutes_played"].sum())
    avg_rating      = round(float(df["rating"].mean()), 2) if len(df) else 0.0
    total_games     = int(df["appearances"].sum())

    st.markdown(
        f"""
        <div class="kpi-row">
          <div class="kpi-card">
            <div class="kpi-label">Total Players</div>
            <div class="kpi-value">{total_players:,}</div>
            <div class="kpi-sub">unique players</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Total Goals</div>
            <div class="kpi-value">{total_goals:,}</div>
            <div class="kpi-sub">{total_games:,} appearances</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Total Assists</div>
            <div class="kpi-value">{total_assists:,}</div>
            <div class="kpi-sub">goal contributions</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Minutes Played</div>
            <div class="kpi-value">{total_minutes:,}</div>
            <div class="kpi-sub">across all seasons</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Avg Rating</div>
            <div class="kpi-value">{avg_rating}</div>
            <div class="kpi-sub">out of 9.5</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────
# HELPER
# ──────────────────────────────────────────────────
def empty_state(msg: str = "No players match the current filters. Adjust the sidebar selections.") -> None:
    st.warning(f"⚠️ {msg}")


def section(title: str) -> None:
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def chart_cfg(fig: go.Figure, height: int = 380) -> go.Figure:
    """Apply consistent dark theme overrides to every chart."""
    fig.update_layout(
        height=height,
        paper_bgcolor="#1e2536",
        plot_bgcolor="#1e2536",
        font=dict(color="#c9d1d9", size=12),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor="#1e2536", borderwidth=0),
    )
    fig.update_xaxes(gridcolor="#2a3550", zerolinecolor="#2a3550")
    fig.update_yaxes(gridcolor="#2a3550", zerolinecolor="#2a3550")
    return fig


# ──────────────────────────────────────────────────
# PAGE 1 — OVERVIEW
# ──────────────────────────────────────────────────
def page_overview(df: pd.DataFrame) -> None:
    st.markdown(
        '<div class="synthetic-banner">⚠️ <strong>Synthetic Data</strong> — '
        "All statistics are artificially generated for demonstration. "
        "They do not represent real players or clubs.</div>",
        unsafe_allow_html=True,
    )

    render_kpi_cards(df)

    if df.empty:
        empty_state()
        return

    col1, col2 = st.columns(2)

    # Top-10 scorers
    with col1:
        section("🏆 Top 10 Goal Scorers")
        top_scorers = (
            df.groupby("player_name", as_index=False)["goals"]
            .sum()
            .nlargest(10, "goals")
            .sort_values("goals")
        )
        fig = px.bar(
            top_scorers, x="goals", y="player_name", orientation="h",
            color="goals", color_continuous_scale=["#1e2536", ACCENT],
            labels={"goals": "Goals", "player_name": ""},
            template=PLOTLY_TEMPLATE,
        )
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(chart_cfg(fig), use_container_width=True)

    # Top-10 assisters
    with col2:
        section("🎯 Top 10 Assisters")
        top_assists = (
            df.groupby("player_name", as_index=False)["assists"]
            .sum()
            .nlargest(10, "assists")
            .sort_values("assists")
        )
        fig2 = px.bar(
            top_assists, x="assists", y="player_name", orientation="h",
            color="assists", color_continuous_scale=["#1e2536", "#1de9b6"],
            labels={"assists": "Assists", "player_name": ""},
            template=PLOTLY_TEMPLATE,
        )
        fig2.update_coloraxes(showscale=False)
        st.plotly_chart(chart_cfg(fig2), use_container_width=True)

    col3, col4 = st.columns(2)

    # Position distribution donut
    with col3:
        section("📊 Players by Position")
        pos_counts = df.groupby("position")["player_id"].nunique().reset_index()
        pos_counts.columns = ["position", "count"]
        fig3 = px.pie(
            pos_counts, values="count", names="position",
            hole=0.55, color_discrete_sequence=GREEN_PALETTE,
            template=PLOTLY_TEMPLATE,
        )
        fig3.update_traces(textposition="outside", textinfo="label+percent")
        st.plotly_chart(chart_cfg(fig3, height=360), use_container_width=True)

    # Goals by team per season
    with col4:
        section("⚽ Goals by Team & Season")
        team_season = (
            df.groupby(["team", "season"], as_index=False)["goals"].sum()
        )
        fig4 = px.bar(
            team_season, x="team", y="goals", color="season",
            barmode="group", color_discrete_sequence=GREEN_PALETTE,
            labels={"goals": "Goals", "team": "", "season": "Season"},
            template=PLOTLY_TEMPLATE,
        )
        fig4.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(chart_cfg(fig4, height=360), use_container_width=True)


# ──────────────────────────────────────────────────
# PAGE 2 — PLAYER ANALYSIS
# ──────────────────────────────────────────────────
def page_player(df: pd.DataFrame) -> None:
    if df.empty:
        empty_state()
        return

    # Aggregate across seasons for per-player totals
    agg = (
        df.groupby(["player_id", "player_name", "team", "position"], as_index=False)
        .agg(
            goals=("goals", "sum"),
            assists=("assists", "sum"),
            shots=("shots", "sum"),
            shots_on_target=("shots_on_target", "sum"),
            passes=("passes", "sum"),
            pass_accuracy=("pass_accuracy", "mean"),
            tackles=("tackles", "sum"),
            minutes_played=("minutes_played", "sum"),
            appearances=("appearances", "sum"),
            rating=("rating", "mean"),
        )
    )
    agg["rating"] = agg["rating"].round(2)
    agg["pass_accuracy"] = agg["pass_accuracy"].round(1)

    # ── Radar comparison ──
    section("📡 Player Attribute Comparison (Radar)")
    all_names = sorted(agg["player_name"].unique().tolist())
    selected = st.multiselect(
        "Select 2–5 players to compare",
        all_names,
        default=all_names[:3] if len(all_names) >= 3 else all_names,
        max_selections=5,
        key="radar_select",
    )

    if len(selected) < 2:
        st.info("ℹ️ Select at least 2 players to display the radar chart.")
    else:
        radar_df = agg[agg["player_name"].isin(selected)].copy()
        # Normalise each metric 0–1 across selected players for fair comparison
        metrics = ["goals", "assists", "passes", "tackles", "rating"]
        labels  = ["Goals", "Assists", "Passes", "Tackles", "Rating"]

        fig_radar = go.Figure()
        for _, row in radar_df.iterrows():
            values = [
                row[m] / agg[m].max() if agg[m].max() > 0 else 0
                for m in metrics
            ]
            values += [values[0]]  # close polygon
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=values,
                    theta=labels + [labels[0]],
                    fill="toself",
                    name=row["player_name"],
                    opacity=0.75,
                )
            )
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1], gridcolor="#2a3550", color="#8899aa"),
                angularaxis=dict(gridcolor="#2a3550"),
                bgcolor="#1e2536",
            ),
            showlegend=True,
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(chart_cfg(fig_radar, height=450), use_container_width=True)

    col1, col2 = st.columns(2)

    # Goals vs Assists scatter
    with col1:
        section("🎯 Goals vs Assists")
        fig_ga = px.scatter(
            agg, x="goals", y="assists", color="position",
            size="minutes_played", hover_name="player_name",
            hover_data={"team": True, "position": True, "rating": True, "minutes_played": False},
            color_discrete_sequence=GREEN_PALETTE,
            labels={"goals": "Goals", "assists": "Assists", "position": "Position"},
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(chart_cfg(fig_ga), use_container_width=True)

    # Shots vs Goals scatter (manual numpy trendline — no statsmodels needed)
    with col2:
        section("🔫 Shots vs Goals")
        fig_sg = px.scatter(
            agg, x="shots", y="goals", color="position",
            hover_name="player_name",
            hover_data={"team": True, "shots_on_target": True, "position": True},
            color_discrete_sequence=GREEN_PALETTE,
            labels={"shots": "Shots", "goals": "Goals", "position": "Position"},
            template=PLOTLY_TEMPLATE,
        )
        # Add a simple linear trendline using numpy polyfit
        _x = agg["shots"].to_numpy(dtype=float)
        _y = agg["goals"].to_numpy(dtype=float)
        if len(_x) >= 2:
            _m, _b = np.polyfit(_x, _y, 1)
            _xr = np.array([_x.min(), _x.max()])
            fig_sg.add_trace(
                go.Scatter(
                    x=_xr, y=_m * _xr + _b,
                    mode="lines",
                    line=dict(color="#ffffff", width=1, dash="dot"),
                    name="Trend",
                    showlegend=False,
                )
            )
        st.plotly_chart(chart_cfg(fig_sg), use_container_width=True)

    # Rating leaderboard
    section("⭐ Player Rating Leaderboard (Top 15)")
    top_rated = agg.nlargest(15, "rating").sort_values("rating")
    fig_rate = px.bar(
        top_rated, x="rating", y="player_name", orientation="h",
        color="rating", color_continuous_scale=["#1e2536", ACCENT],
        hover_data={"team": True, "position": True, "goals": True, "assists": True},
        labels={"rating": "Avg Rating", "player_name": ""},
        template=PLOTLY_TEMPLATE,
    )
    fig_rate.update_coloraxes(showscale=False)
    fig_rate.update_xaxes(range=[5.5, 10])
    st.plotly_chart(chart_cfg(fig_rate, height=420), use_container_width=True)


# ──────────────────────────────────────────────────
# PAGE 3 — TEAM ANALYSIS
# ──────────────────────────────────────────────────
def page_team(df: pd.DataFrame) -> None:
    if df.empty:
        empty_state()
        return

    team_agg = df.groupby("team", as_index=False).agg(
        goals=("goals", "sum"),
        assists=("assists", "sum"),
        players=("player_id", "nunique"),
        avg_rating=("rating", "mean"),
        yellow_cards=("yellow_cards", "sum"),
        red_cards=("red_cards", "sum"),
    )
    team_agg["avg_rating"] = team_agg["avg_rating"].round(2)

    col1, col2, col3 = st.columns(3)

    with col1:
        section("⚽ Total Goals by Team")
        fig1 = px.bar(
            team_agg.sort_values("goals", ascending=False),
            x="team", y="goals", color="goals",
            color_continuous_scale=["#1e2536", ACCENT],
            labels={"goals": "Goals", "team": ""},
            template=PLOTLY_TEMPLATE,
        )
        fig1.update_coloraxes(showscale=False)
        st.plotly_chart(chart_cfg(fig1, height=320), use_container_width=True)

    with col2:
        section("🎯 Total Assists by Team")
        fig2 = px.bar(
            team_agg.sort_values("assists", ascending=False),
            x="team", y="assists", color="assists",
            color_continuous_scale=["#1e2536", "#1de9b6"],
            labels={"assists": "Assists", "team": ""},
            template=PLOTLY_TEMPLATE,
        )
        fig2.update_coloraxes(showscale=False)
        st.plotly_chart(chart_cfg(fig2, height=320), use_container_width=True)

    with col3:
        section("👥 Squad Size by Team")
        fig3 = px.bar(
            team_agg.sort_values("players", ascending=False),
            x="team", y="players", color="players",
            color_continuous_scale=["#1e2536", "#aeea00"],
            labels={"players": "Players", "team": ""},
            template=PLOTLY_TEMPLATE,
        )
        fig3.update_coloraxes(showscale=False)
        st.plotly_chart(chart_cfg(fig3, height=320), use_container_width=True)

    col4, col5 = st.columns(2)

    # Goals across seasons — line chart
    with col4:
        section("📈 Team Goals Across Seasons")
        ts = df.groupby(["team", "season"], as_index=False)["goals"].sum()
        fig4 = px.line(
            ts, x="season", y="goals", color="team",
            markers=True, color_discrete_sequence=GREEN_PALETTE,
            labels={"goals": "Goals", "season": "Season", "team": "Team"},
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(chart_cfg(fig4, height=360), use_container_width=True)

    # Avg rating heatmap by team × position
    with col5:
        section("🌡️ Avg Rating: Team × Position")
        heat_df = df.groupby(["team", "position"], as_index=False)["rating"].mean().round(2)
        heat_pivot = heat_df.pivot(index="team", columns="position", values="rating")
        # Ensure consistent column order
        for p in POSITIONS:
            if p not in heat_pivot.columns:
                heat_pivot[p] = np.nan
        heat_pivot = heat_pivot[POSITIONS]

        fig5 = go.Figure(
            go.Heatmap(
                z=heat_pivot.values,
                x=heat_pivot.columns.tolist(),
                y=heat_pivot.index.tolist(),
                colorscale=[[0, "#1e2536"], [0.5, "#007030"], [1, ACCENT]],
                text=heat_pivot.values.round(2),
                texttemplate="%{text}",
                hovertemplate="Team: %{y}<br>Position: %{x}<br>Avg Rating: %{z:.2f}<extra></extra>",
            )
        )
        st.plotly_chart(chart_cfg(fig5, height=360), use_container_width=True)


# ──────────────────────────────────────────────────
# PAGE 4 — POSITION ANALYSIS
# ──────────────────────────────────────────────────
def page_position(df: pd.DataFrame) -> None:
    if df.empty:
        empty_state()
        return

    tab_gk, tab_def, tab_mid, tab_fwd = st.tabs(["🧤 Goalkeeper", "🛡️ Defender", "⚙️ Midfielder", "⚡ Forward"])

    def pos_tab(pos_code: str, pos_label: str) -> None:
        pos_df = df[df["position"] == pos_code]
        if pos_df.empty:
            empty_state(f"No {pos_label} data for current filters.")
            return

        pos_agg = pos_df.groupby(
            ["player_id", "player_name", "team"], as_index=False
        ).agg(
            goals=("goals", "sum"),
            assists=("assists", "sum"),
            passes=("passes", "sum"),
            pass_accuracy=("pass_accuracy", "mean"),
            tackles=("tackles", "sum"),
            clean_sheets=("clean_sheets", "sum"),
            appearances=("appearances", "sum"),
            rating=("rating", "mean"),
        )
        pos_agg["rating"] = pos_agg["rating"].round(2)
        pos_agg["pass_accuracy"] = pos_agg["pass_accuracy"].round(1)

        # KPI strip for this position
        st.markdown(
            f"""
            <div class="kpi-row">
              <div class="kpi-card">
                <div class="kpi-label">Players</div>
                <div class="kpi-value">{pos_agg['player_id'].nunique()}</div>
              </div>
              <div class="kpi-card">
                <div class="kpi-label">Total Goals</div>
                <div class="kpi-value">{int(pos_df['goals'].sum()):,}</div>
              </div>
              <div class="kpi-card">
                <div class="kpi-label">Total Assists</div>
                <div class="kpi-value">{int(pos_df['assists'].sum()):,}</div>
              </div>
              <div class="kpi-card">
                <div class="kpi-label">Avg Rating</div>
                <div class="kpi-value">{pos_df['rating'].mean():.2f}</div>
              </div>
              <div class="kpi-card">
                <div class="kpi-label">Avg Pass Acc.</div>
                <div class="kpi-value">{pos_df['pass_accuracy'].mean():.1f}%</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        # Rating distribution
        with col1:
            section(f"📊 Rating Distribution — {pos_label}")
            fig_box = px.box(
                pos_df, y="rating", x="team",
                color="team", color_discrete_sequence=GREEN_PALETTE,
                labels={"rating": "Rating", "team": ""},
                template=PLOTLY_TEMPLATE,
                points="all",
            )
            fig_box.update_layout(showlegend=False)
            st.plotly_chart(chart_cfg(fig_box), use_container_width=True)

        # Average stats bar
        with col2:
            if pos_code == "GK":
                section("🧤 Clean Sheets Leaderboard")
                top_cs = pos_agg.nlargest(10, "clean_sheets").sort_values("clean_sheets")
                fig_cs = px.bar(
                    top_cs, x="clean_sheets", y="player_name", orientation="h",
                    color="clean_sheets",
                    color_continuous_scale=["#1e2536", ACCENT],
                    labels={"clean_sheets": "Clean Sheets", "player_name": ""},
                    template=PLOTLY_TEMPLATE,
                )
                fig_cs.update_coloraxes(showscale=False)
                st.plotly_chart(chart_cfg(fig_cs), use_container_width=True)
            else:
                section(f"📈 Top 10 by Goals — {pos_label}")
                top_goals = pos_agg.nlargest(10, "goals").sort_values("goals")
                fig_tg = px.bar(
                    top_goals, x="goals", y="player_name", orientation="h",
                    color="goals",
                    color_continuous_scale=["#1e2536", ACCENT],
                    labels={"goals": "Goals", "player_name": ""},
                    template=PLOTLY_TEMPLATE,
                )
                fig_tg.update_coloraxes(showscale=False)
                st.plotly_chart(chart_cfg(fig_tg), use_container_width=True)

        # Pass accuracy vs Rating scatter (DEF & MID) / Appearances vs Rating (FWD/GK)
        col3, col4 = st.columns(2)
        with col3:
            section("🎯 Pass Accuracy vs Rating")
            fig_pa = px.scatter(
                pos_agg, x="pass_accuracy", y="rating",
                color="team", hover_name="player_name",
                hover_data={"goals": True, "assists": True},
                color_discrete_sequence=GREEN_PALETTE,
                labels={"pass_accuracy": "Pass Accuracy (%)", "rating": "Avg Rating"},
                template=PLOTLY_TEMPLATE,
            )
            st.plotly_chart(chart_cfg(fig_pa), use_container_width=True)

        with col4:
            section("📅 Appearances vs Goals")
            fig_ag = px.scatter(
                pos_agg, x="appearances", y="goals",
                color="team", hover_name="player_name",
                size="rating",
                color_discrete_sequence=GREEN_PALETTE,
                labels={"appearances": "Appearances", "goals": "Goals"},
                template=PLOTLY_TEMPLATE,
            )
            st.plotly_chart(chart_cfg(fig_ag), use_container_width=True)

    with tab_gk:
        pos_tab("GK", "Goalkeeper")
    with tab_def:
        pos_tab("DEF", "Defender")
    with tab_mid:
        pos_tab("MID", "Midfielder")
    with tab_fwd:
        pos_tab("FWD", "Forward")


# ──────────────────────────────────────────────────
# PAGE 5 — STATS TABLE
# ──────────────────────────────────────────────────
def page_table(df: pd.DataFrame) -> None:
    if df.empty:
        empty_state()
        return

    section("📋 Player Statistics Table")

    display_cols = [
        "player_name", "team", "position", "season", "age", "nationality",
        "appearances", "minutes_played", "goals", "assists",
        "shots", "shots_on_target", "passes", "pass_accuracy",
        "tackles", "yellow_cards", "red_cards", "clean_sheets", "rating",
    ]
    # Only show columns that exist
    display_cols = [c for c in display_cols if c in df.columns]
    table_df = df[display_cols].copy()

    # Rename for display
    table_df.columns = [c.replace("_", " ").title() for c in table_df.columns]

    st.dataframe(
        table_df,
        use_container_width=True,
        height=520,
        hide_index=True,
    )

    # CSV download
    csv_bytes = df[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="football_players_filtered.csv",
        mime="text/csv",
        help="Downloads the currently filtered dataset",
    )

    st.caption(
        f"Showing **{len(df):,}** rows · "
        f"**{df['player_id'].nunique()}** unique players · "
        f"**{df['team'].nunique()}** teams"
    )


# ──────────────────────────────────────────────────
# MAIN — navigation & page dispatch
# ──────────────────────────────────────────────────
def main() -> None:
    inject_css()

    df_raw = load_data()
    df = render_sidebar(df_raw)

    # Navigation
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "📂 Navigate",
        [
            "🏠 Overview",
            "👤 Player Analysis",
            "🏟️ Team Analysis",
            "📍 Position Analysis",
            "📋 Stats Table",
        ],
        key="nav_page",
    )

    # Page title
    st.markdown(
        f"<h1 style='color:#e6edf3;font-size:26px;margin-bottom:4px;'>{page}</h1>"
        f"<p style='color:#57606a;font-size:13px;margin-bottom:20px;'>"
        f"Showing data for "
        f"<span style='color:#00c853'>{df['player_id'].nunique()} players</span> "
        f"across "
        f"<span style='color:#00c853'>{df['team'].nunique()} teams</span>"
        f"</p>",
        unsafe_allow_html=True,
    )

    if page == "🏠 Overview":
        page_overview(df)
    elif page == "👤 Player Analysis":
        page_player(df)
    elif page == "🏟️ Team Analysis":
        page_team(df)
    elif page == "📍 Position Analysis":
        page_position(df)
    elif page == "📋 Stats Table":
        page_table(df)

    # Footer
    st.sidebar.markdown(
        "<div style='position:fixed;bottom:16px;left:0;width:260px;"
        "text-align:center;font-size:11px;color:#3d4f6e;padding:0 12px;'>"
        "⚽ Football Analytics Dashboard<br>"
        "<span style='color:#2a3550;'>Synthetic data · For demonstration only</span>"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

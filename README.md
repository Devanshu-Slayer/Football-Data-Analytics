# ⚽ Football Player Performance Analytics Dashboard

> **⚠️ Synthetic Data Notice:** All player statistics in this project are artificially generated for demonstration purposes. They do not represent real-world football players, clubs, or match results.

An interactive football (soccer) analytics dashboard built with Python and Streamlit. Analyse and compare player performance, explore team statistics, and drill down by position — all from a clean, modern, football-inspired dark UI.

---

## Features

- **Overview Page** — KPI cards for total players, goals, assists, minutes played and average rating
- **Player Analysis** — Radar comparison chart, Goals vs Assists scatter, Shots vs Goals scatter, rating leaderboard
- **Team Analysis** — Team-level goals, assists, squad size, season trends and a rating heatmap
- **Position Analysis** — Dedicated tabs for GK, DEF, MID, FWD with position-specific charts
- **Stats Table** — Searchable, sortable player statistics table with CSV export
- **Sidebar Filters** — Season, team, position, player name search and minimum appearances slider
- **Dark Pitch Theme** — Stadium-green accent (`#00c853`) on Streamlit's dark background

---

## Prerequisites

- Python 3.9 or higher
- pip

---

## Local Setup

```bash
# 1. Clone or download the project
git clone https://github.com/your-username/football-analytics-dashboard.git
cd football-analytics-dashboard

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**.

> The first run generates `football_players.csv` automatically. Do not delete it while the app is running.

---

## Deploy to Streamlit Community Cloud

1. Push your project to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select your repository → set **Main file path** to `app.py`.
4. Click **Deploy**. Streamlit will install dependencies from `requirements.txt` automatically.

---

## Dataset Schema

| Column | Type | Description |
|---|---|---|
| player_id | int | Unique player identifier (1–120) |
| player_name | str | Synthetic player name |
| team | str | One of 6 clubs |
| position | str | GK · DEF · MID · FWD |
| season | str | 2021-22 · 2022-23 · 2023-24 |
| age | int | 17–35 |
| nationality | str | 15 nationalities |
| appearances | int | Matches played (1–38) |
| minutes_played | int | Total minutes in season |
| goals | int | Goals scored |
| assists | int | Goal assists |
| shots | int | Total shots |
| shots_on_target | int | Shots on target |
| passes | int | Total passes |
| pass_accuracy | float | Pass accuracy % (60–95) |
| tackles | int | Total tackles |
| yellow_cards | int | Yellow cards received |
| red_cards | int | Red cards received |
| clean_sheets | int | Clean sheets (GK/DEF only) |
| rating | float | Overall match rating (6.0–9.5) |

---

## Project Structure

```
football-analytics-dashboard/
├── app.py                  # Main Streamlit application
├── football_players.csv    # Auto-generated synthetic dataset
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## License

MIT — free to use, modify and distribute.

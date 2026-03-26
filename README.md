# ⚽ Football Tipster

An automated football betting tip generation and validation system built with Python, PostgreSQL (Supabase), and GitHub Actions. The pipeline runs daily, ingests live match and standings data, applies rule-based logic to generate tips, and tracks prediction accuracy over time.

---

## How It Works

```
football-data.org API
        │
        ▼
  GitHub Actions (daily cron)
        │
        ├── sync_matches.py    ← fetch & upsert match data
        ├── sync_standings.py  ← fetch & upsert league tables
        │
        ▼
  generate_tips.py             ← apply rules, produce tips
        │
        ▼
  validate_tips.py             ← score finished tips WIN/LOSS
        │
        ▼
  Supabase (PostgreSQL)        ← persists everything
        │
        ▼
  Next.js Frontend (Vercel)    ← dashboard, results, stats
```

---

## Features

- **Automated ETL** — daily sync of matches and standings across 9 competitions via GitHub Actions
- **Rule-based tip engine** — 6 layered rules filtering for high-confidence opportunities
- **Form analysis** — last-7-match form strings (e.g. `WWDLWDW..`) computed per team
- **Tip validation** — automatic WIN/LOSS scoring once matches finish
- **Performance stats** — win rate breakdown by prediction type, competition, and confidence level
- **Zero-cost production stack** — Supabase + GitHub Actions + Vercel, all on free tiers

---

## Tip Generation Rules

| Rule | Description |
|------|-------------|
| **Rule 1** | Points difference between teams must be ≥ 10 |
| **Rule 2** | Clear favourite identified by league position (top 7 home or top 4 away) |
| **Rule 3** | Favourite must have ≥ 4 days rest since last match |
| **Rule 4** | Favourite must have no important match (CL, Cup) within 3 days |
| **Rule 5** | Neither team appears on the blacklist |
| **Rule 6** | Favourite must not have 3+ losses in their last 7 matches |

### Prediction Types

| Prediction | Meaning | Condition |
|------------|---------|-----------|
| `1-DNB` | Back home team, Draw No Bet | Home favourite, rested, no important match |
| `2-DNB` | Back away team, Draw No Bet | Away favourite, rested, no important match |
| `1X` | Home win or Draw | Home favourite, not fully rested |
| `X2` | Draw or Away win | Away favourite, not fully rested |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11 |
| Database | PostgreSQL via Supabase |
| Scheduling | GitHub Actions (cron) |
| Data source | football-data.org API |
| Frontend | Next.js + Supabase JS client |
| Hosting | Vercel (frontend) · GitHub Actions (ETL) |

---

## Project Structure

```
football_tipster/
│
├── .github/
│   └── workflows/
│       └── etl.yml           ← scheduled pipeline
│
├── api/
│   └── football_api.py       ← rate-limited API client
│
├── config/
│   └── settings.py           ← env-var based config
│
├── database/
│   ├── db.py                 ← psycopg2 connection
│   └── schema.sql            ← table definitions
│
├── etl/
│   ├── sync_matches.py       ← match ingestion
│   ├── sync_standings.py     ← standings ingestion
│   └── sync_teams.py         ← team upsert helper
│
├── features/
│   └── form.py               ← last-7-match form computation
│
├── migrations/
│   ├── add_form_columns.sql
│   └── create_tip_results.sql
│
├── tipster/
│   ├── generate_tips.py      ← tip generation engine
│   └── validate_tips.py      ← WIN/LOSS validation
│
├── app/                      ← Next.js frontend
│
├── main.py                   ← pipeline entry point
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Competitions Covered

| Code | League |
|------|--------|
| PL | Premier League (England) |
| CL | Champions League (Europe) |
| BL1 | Bundesliga (Germany) |
| PD | La Liga (Spain) |
| SA | Serie A (Italy) |
| FL1 | Ligue 1 (France) |
| DED | Eredivisie (Netherlands) |
| PPL | Primeira Liga (Portugal) |
| ELC | Championship (England) |

---

## Local Setup

**1. Clone the repo**
```bash
git clone https://github.com/mulongocheloti/football_tipster.git
cd football_tipster
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Create your `.env` file**
```bash
cp .env.example .env
# Fill in API_TOKEN and DATABASE_URL
```

**4. Run the schema against your database**
```sql
-- Run in order:
-- database/schema.sql
-- migrations/add_form_columns.sql
-- migrations/create_tip_results.sql
```

**5. Run the pipeline**
```bash
python main.py
```

---

## Production Deployment

| Component | Service | Cost |
|-----------|---------|------|
| Database | Supabase (free tier) | $0 |
| ETL scheduling | GitHub Actions (free tier) | $0 |
| Frontend hosting | Vercel (free tier) | $0 |

The pipeline runs automatically every day at **06:00 UTC** via GitHub Actions. Secrets (`DATABASE_URL`, `API_TOKEN`) are stored in GitHub repository secrets and never committed to code.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `API_TOKEN` | football-data.org API key |
| `DATABASE_URL` | PostgreSQL connection string (Supabase pooler URL) |

For the Next.js frontend:

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase public anon key |

---

## Database Schema

```sql
teams           -- team_id, team_name
matches         -- match data, scores, status
standings       -- league table per competition per season
tips            -- generated tips with form strings and flags
tip_results     -- validated outcomes (WIN/LOSS) with actual scores
team_blacklist  -- teams excluded from tip generation
api_sync_log    -- tracks last sync per competition to avoid redundant calls
```

---

## Author

**Paul Cheloti Mulongo**
Built as a personal data engineering project — from local Python scripts to a fully automated production pipeline.

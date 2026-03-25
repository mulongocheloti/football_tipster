from datetime import datetime, UTC, timedelta
from api.football_api import FootballAPI
from config.settings import BASE_URL
from database.db import get_connection
from etl.sync_teams import store_team

def sync_matches(competition, season):

    api=FootballAPI()

    today=datetime.now(UTC).date()

    # use this when you want to only pull last 7 days + next 7 days
    date_from=today-timedelta(days=7)
    date_to=today+timedelta(days=7)

    url=f"{BASE_URL}/competitions/{competition}/matches"

    if competition == "CL":
        data = api.get(url) #API endpoint does not support the 'season' parameter for UCL
    else:
        data = api.get(url,{
            "dateFrom":date_from,
            "dateTo":date_to,
            "season":season
        })

    conn=get_connection()
    cur=conn.cursor()

    for m in data["matches"]:

        home = m.get("homeTeam")
        away = m.get("awayTeam")

        if not home or not away:
            continue

        if home.get("id") is None or away.get("id") is None:
            continue

        store_team(home)
        store_team(away)

        cur.execute("""
        INSERT INTO matches
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT(match_id)
        DO UPDATE SET
        home_goals=EXCLUDED.home_goals,
        away_goals=EXCLUDED.away_goals,
        status=EXCLUDED.status
        """,(
        m["id"],
        competition,
        season,
        m["utcDate"],
        m["matchday"],
        m["homeTeam"]["id"],
        m["awayTeam"]["id"],
        m["score"]["fullTime"]["home"],
        m["score"]["fullTime"]["away"],
        m["status"]
        ))

    conn.commit()

    cur.close()
    conn.close()
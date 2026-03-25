from datetime import datetime, UTC, timedelta
import pandas as pd
from api.football_api import FootballAPI
from config.settings import BASE_URL
from database.db import get_connection

# api provides current season data only
def sync_standings(competition, season):

    conn=get_connection()

    log=pd.read_sql(
    """
    SELECT last_standings_sync
    FROM api_sync_log
    WHERE competition_code=%s
    AND season=%s
    """,
    conn,
    params=[competition,season]
    )

    if not log.empty and log.iloc[0].last_standings_sync:

        if log.iloc[0].last_standings_sync.date()==datetime.utcnow().date():

            print("Standings already synced:",competition)
            return

    api=FootballAPI()

    url=f"{BASE_URL}/competitions/{competition}/standings"

    if competition == "CL":
        data = api.get(url) #API endpoint does not support the 'season' parameter for UCL
    else:
        data = api.get(url,{
            "season":season
        })

    table=data["standings"][0]["table"]

    cur=conn.cursor()

    for t in table:

        cur.execute("""
        INSERT INTO standings
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT(competition_code,team_id,season)
        DO UPDATE SET
        position=EXCLUDED.position,
        points=EXCLUDED.points
        """,(
        competition,
        t["team"]["id"],
        season,
        t["position"],
        t["playedGames"],
        t["won"],
        t["draw"],
        t["lost"],
        t["points"]
        ))

    cur.execute("""
    INSERT INTO api_sync_log(competition_code,season,last_standings_sync)
    VALUES(%s,%s,NOW())
    ON CONFLICT(competition_code,season)
    DO UPDATE SET last_standings_sync=NOW()
    """,(competition,season))

    conn.commit()

    cur.close()
    conn.close()
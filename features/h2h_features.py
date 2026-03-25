# Head-to-Head Feature --- not used yet

import pandas as pd
from database.db import get_connection


def get_h2h(home, away):

    conn = get_connection()

    df = pd.read_sql(
    """
    SELECT *
    FROM matches
    WHERE
    (home_team_id=%s AND away_team_id=%s)
    OR
    (home_team_id=%s AND away_team_id=%s)
    ORDER BY utc_date DESC
    LIMIT 5
    """,
    conn,
    params=(home,away,away,home)
    )

    return df
import pandas as pd


def get_form(team_id, before_date, conn):
    """
    Return the last-7-finished-matches form for a team, computed across ALL
    competitions (so cup & league results are both counted, matching real-world
    form perception).

    Parameters
    ----------
    team_id   : int   – the team whose form we want
    before_date: datetime-like – only consider matches played before this moment
    conn      : psycopg2 connection – shared caller connection (not closed here)

    Returns
    -------
    form_str  : str  – up to 7 chars + ".." suffix, most-recent result first
                       e.g. "WWDLWDW.."  or "WLD.." if fewer than 7 played
    loss_count: int  – number of L's in form_str (excluding the "..")
    """

    rows = pd.read_sql("""
        SELECT
            match_id,
            home_team_id,
            away_team_id,
            home_goals,
            away_goals
        FROM matches
        WHERE status = 'FINISHED'
          AND (home_team_id = %s OR away_team_id = %s)
          AND utc_date < %s
        ORDER BY utc_date DESC
        LIMIT 7
    """, conn, params=[team_id, team_id, before_date])

    chars = []

    for _, row in rows.iterrows():

        is_home = (row["home_team_id"] == team_id)

        hg = row["home_goals"]
        ag = row["away_goals"]

        # Treat NULL scores (postponed/abandoned edge cases) as draws
        if hg is None or ag is None:
            chars.append("D")
            continue

        if is_home:
            if hg > ag:
                chars.append("W")
            elif hg < ag:
                chars.append("L")
            else:
                chars.append("D")
        else:
            if ag > hg:
                chars.append("W")
            elif ag < hg:
                chars.append("L")
            else:
                chars.append("D")

    form_str = "".join(chars) + ".."
    loss_count = chars.count("L")

    return form_str, loss_count

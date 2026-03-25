from database.db import get_connection

def store_team(team):

    # skip invalid teams
    if not team:
        return

    if team.get("id") is None or team.get("name") is None:
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO teams(team_id,team_name)
    VALUES(%s,%s)
    ON CONFLICT DO NOTHING
    """,(team["id"],team["name"]))

    conn.commit()

    cur.close()
    conn.close()
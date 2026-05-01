import pandas as pd
from datetime import datetime, UTC, timedelta
from database.db import get_connection
from features.compute_form import get_form


def generate():

    conn = get_connection()

    today = datetime.now(UTC).date()
    future = today + timedelta(days=10)

    matches = pd.read_sql("""
        SELECT *
        FROM matches
        WHERE status IN ('TIMED','SCHEDULED')
        AND DATE(utc_date) >= %s
        AND DATE(utc_date) <= %s
    """, conn, params=[today, future])

    standings = pd.read_sql("SELECT * FROM standings WHERE season = (SELECT MAX(season) FROM standings)", conn)

    blacklist = pd.read_sql("SELECT team_id FROM team_blacklist", conn)
    blacklist_ids = set(blacklist["team_id"].values)

    tips = []

    for _, m in matches.iterrows():

        home = m["home_team_id"]
        away = m["away_team_id"]
        comp = m["competition_code"]

        # Changes - Remove this hard skip RULE 5 blacklist
        # if home in blacklist_ids or away in blacklist_ids:
        #    continue

        home_row = standings[
            (standings.team_id == home) &
            (standings.competition_code == comp)
        ]

        away_row = standings[
            (standings.team_id == away) &
            (standings.competition_code == comp)
        ]

        if home_row.empty or away_row.empty:
            continue

        home_points = int(home_row.iloc[0].points)
        away_points = int(away_row.iloc[0].points)

        home_pos = int(home_row.iloc[0].position)
        away_pos = int(away_row.iloc[0].position)

        points_diff = abs(home_points - away_points)

        # RULE 1
        if points_diff < 10:
            continue

        # RULE 2 favourite logic
        favourite = None
        fav_side = None

        if home_pos <= 7 and away_pos > 7:
            favourite = home
            fav_side = "home"

        elif home_pos > 7 and away_pos <= 4:
            favourite = away
            fav_side = "away"

        else:
            continue

        # FORM – compute for both sides before the match kick-off
        home_form, home_losses = get_form(home, m.utc_date, conn)
        away_form, away_losses = get_form(away, m.utc_date, conn)

        fav_losses = home_losses if fav_side == "home" else away_losses

        # RULE 6 – skip if favourite is badly out of form (3+ losses in last 7)
        if fav_losses >= 3:
            continue

        # RULE 3 rest check
        last_match = pd.read_sql("""
            SELECT utc_date
            FROM matches
            WHERE status='FINISHED'
            AND (home_team_id=%s OR away_team_id=%s)
            ORDER BY utc_date DESC
            LIMIT 1
        """, conn, params=[favourite, favourite])

        rested = False

        if not last_match.empty:
            last_played = last_match.iloc[0].utc_date.date()
            rest_days = (m.utc_date.date() - last_played).days

            if rest_days >= 4:
                rested = True

        # RULE 4 upcoming important match
        important_comps = ("CL","ELC","FA","CIT","CDF")

        upcoming = pd.read_sql("""
            SELECT match_id
            FROM matches
            WHERE competition_code IN %s
            AND status IN ('TIMED','SCHEDULED')
            AND utc_date > %s
            AND utc_date <= %s
            AND (home_team_id=%s OR away_team_id=%s)
        """, conn, params=[
            important_comps,
            m.utc_date,
            m.utc_date + timedelta(days=3),
            favourite,
            favourite
        ])

        no_important_match = upcoming.empty

        # FLAG construction
        flag_parts = []

        if not rested:
            flag_parts.append("not rested")

        if not no_important_match:
            flag_parts.append("important match coming")

        # Check if the FAVOURITE is blacklisted
        if favourite in blacklist_ids:
            flag_parts.append("blacklisted")

        flag = ", ".join(flag_parts)

        # PREDICTION logic
        if fav_side == "home":

            if rested and no_important_match:
                prediction = "1-DNB"
            else:
                prediction = "1X"

        else:

            if rested and no_important_match:
                prediction = "2-DNB"
            else:
                prediction = "X2"

        # CONFIDENCE scoring
        confidence = 0

        if points_diff >= 20:
            confidence += 2
        elif points_diff >= 15:
            confidence += 1

        if rested:
            confidence += 1

        if no_important_match:
            confidence += 1

        if fav_side == "home" and home_pos <= 4:
            confidence += 1

        if fav_side == "away" and away_pos <= 2:
            confidence += 1

        tips.append({
            "match_id": m.match_id,
            "utc_date": m.utc_date,
            "home_position": home_pos,
            "away_position": away_pos,
            "points_difference": points_diff,
            "prediction": prediction,
            "confidence": confidence,
            "flag": flag,
            "home_form": home_form,
            "away_form": away_form
        })

    tips_df = pd.DataFrame(tips)
    print("Tips generated:", len(tips_df))

    cur = conn.cursor()
    for _, row in tips_df.iterrows():

        cur.execute("""
            INSERT INTO tips(
                match_id,
                utc_date,
                home_position,
                away_position,
                points_difference,
                prediction,
                confidence,
                flag,
                home_form,
                away_form
            )
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

            ON CONFLICT(match_id)
            DO UPDATE SET

            utc_date           = EXCLUDED.utc_date,
            home_position      = EXCLUDED.home_position,
            away_position      = EXCLUDED.away_position,
            points_difference  = EXCLUDED.points_difference,
            prediction         = EXCLUDED.prediction,
            confidence         = EXCLUDED.confidence,
            flag               = EXCLUDED.flag,
            home_form          = EXCLUDED.home_form,
            away_form          = EXCLUDED.away_form
        """, (
            row.match_id,
            row.utc_date,
            row.home_position,
            row.away_position,
            row.points_difference,
            row.prediction,
            row.confidence,
            row.flag,
            row.home_form,
            row.away_form
        ))

    conn.commit()

    cur.close()
    conn.close()

    print("Tips saved:", len(tips_df))

if __name__ == "__main__":
    generate()

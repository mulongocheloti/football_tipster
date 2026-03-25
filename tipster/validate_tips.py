import pandas as pd
from database.db import get_connection


# ---------------------------------------------------------------------------
# Prediction evaluation
# ---------------------------------------------------------------------------

def evaluate(prediction: str, home_goals: int, away_goals: int) -> tuple[str, str]:
    """
    Return (actual_result, outcome).

    actual_result : "HOME_WIN" | "DRAW" | "AWAY_WIN"
    outcome       : "WIN"      | "LOSS"
    """

    if home_goals > away_goals:
        actual_result = "HOME_WIN"
    elif home_goals < away_goals:
        actual_result = "AWAY_WIN"
    else:
        actual_result = "DRAW"

    if prediction == "1-DNB":
        outcome = "WIN" if actual_result == "HOME_WIN" else "ODD FLAT" if actual_result == "DRAW" else "LOSS"

    elif prediction == "2-DNB":
        outcome = "WIN" if actual_result == "AWAY_WIN" else "ODD FLAT" if actual_result == "DRAW" else "LOSS"

    elif prediction == "1X":
        outcome = "WIN" if actual_result in ("HOME_WIN", "DRAW") else "LOSS"

    elif prediction == "X2":
        outcome = "WIN" if actual_result in ("AWAY_WIN", "DRAW") else "LOSS"

    else:
        # Unknown prediction type — treat as loss so it surfaces for review
        outcome = "LOSS"

    return actual_result, outcome


# ---------------------------------------------------------------------------
# Main validation routine
# ---------------------------------------------------------------------------

def validate():

    conn = get_connection()

    # Pull tips that have a finished match but are NOT yet in tip_results
    pending = pd.read_sql("""
        SELECT
            t.match_id,
            t.utc_date,
            t.prediction,
            t.confidence,
            t.flag,
            t.home_form,
            t.away_form,
            m.competition_code,
            m.home_team_id,
            m.away_team_id,
            m.home_goals,
            m.away_goals,
            ht.team_name AS home_team,
            at.team_name AS away_team
        FROM tips t
        JOIN matches m
            ON m.match_id = t.match_id
           AND m.status   = 'FINISHED'
           AND m.home_goals IS NOT NULL
           AND m.away_goals IS NOT NULL
        JOIN teams ht ON ht.team_id = m.home_team_id
        JOIN teams at ON at.team_id = m.away_team_id
        LEFT JOIN tip_results tr ON tr.match_id = t.match_id
        WHERE tr.match_id IS NULL
        ORDER BY t.utc_date ASC
    """, conn)

    if pending.empty:
        print("No new tips to validate.")
        conn.close()
        return

    print(f"Validating {len(pending)} tip(s)...")

    records = []

    for _, row in pending.iterrows():

        actual_result, outcome = evaluate(
            row["prediction"],
            int(row["home_goals"]),
            int(row["away_goals"])
        )

        records.append({
            "match_id":        row["match_id"],
            "utc_date":        row["utc_date"],
            "competition_code": row["competition_code"],
            "home_team":       row["home_team"],
            "away_team":       row["away_team"],
            "home_goals":      int(row["home_goals"]),
            "away_goals":      int(row["away_goals"]),
            "actual_result":   actual_result,
            "prediction":      row["prediction"],
            "confidence":      row["confidence"],
            "flag":            row["flag"],
            "home_form":       row.get("home_form"),
            "away_form":       row.get("away_form"),
            "outcome":         outcome,
        })

    cur = conn.cursor()

    for r in records:
        cur.execute("""
            INSERT INTO tip_results (
                match_id,
                utc_date,
                competition_code,
                home_team,
                away_team,
                home_goals,
                away_goals,
                actual_result,
                prediction,
                confidence,
                flag,
                home_form,
                away_form,
                outcome,
                validated_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, NOW())
            ON CONFLICT (match_id)
            DO UPDATE SET
                actual_result  = EXCLUDED.actual_result,
                outcome        = EXCLUDED.outcome,
                validated_at   = NOW()
        """, (
            r["match_id"],
            r["utc_date"],
            r["competition_code"],
            r["home_team"],
            r["away_team"],
            r["home_goals"],
            r["away_goals"],
            r["actual_result"],
            r["prediction"],
            r["confidence"],
            r["flag"],
            r["home_form"],
            r["away_form"],
            r["outcome"],
        ))

    conn.commit()
    cur.close()

    # ---------------------------------------------------------------------------
    # Summary report
    # ---------------------------------------------------------------------------

    results_df = pd.DataFrame(records)

    total  = len(results_df)
    wins   = (results_df["outcome"] == "WIN").sum()
    losses = (results_df["outcome"] == "LOSS").sum()
    odd_flattened = (results_df["outcome"] == "ODD FLAT").sum()
    rate   = round(wins / (total-odd_flattened) * 100, 1) if total else 0

    print("\n" + "=" * 52)
    print("  VALIDATION SUMMARY")
    print("=" * 52)
    print(f"  Tips validated : {total}")
    print(f"  Wins           : {wins}")
    print(f"  Odds Flattened : {odd_flattened}")
    print(f"  Losses         : {losses}")
    print(f"  Win rate       : {rate}%")
    print("=" * 52)

    # Per-prediction-type breakdown
    breakdown = (
        results_df
        .groupby("prediction")["outcome"]
        .value_counts()
        .unstack(fill_value=0)
        .rename(columns={"WIN": "W", "LOSS": "L", "ODD FLAT":"F"})
    )
    breakdown["Total"] = breakdown.get("W", 0) + breakdown.get("L", 0)
    breakdown["Win%"]  = (
        breakdown.get("W", 0) / breakdown["Total"] * 100
    ).round(1)

    print("\n  By prediction type:\n")
    print(breakdown.to_string())
    print()

    # Per-competition breakdown
    comp_breakdown = (
        results_df
        .groupby("competition_code")["outcome"]
        .value_counts()
        .unstack(fill_value=0)
        .rename(columns={"WIN": "W", "LOSS": "L"})
    )
    comp_breakdown["Total"] = comp_breakdown.get("W", 0) + comp_breakdown.get("L", 0)
    comp_breakdown["Win%"]  = (
        comp_breakdown.get("W", 0) / comp_breakdown["Total"] * 100
    ).round(1)

    print("  By competition:\n")
    print(comp_breakdown.to_string())
    print()

    conn.close()


if __name__ == "__main__":
    validate()

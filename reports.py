# reports.py
from db import get_connection

def list_patients_with_latest_risk():
      with get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT p.id, p.name, p.external_id, p.smoker,
                           rs.score, rs.risk_band, rs.score_date
                    FROM patients p
                    LEFT JOIN risk_scores rs
                      ON rs.patient_id = p.id
                      AND rs.score_date = (
                          SELECT MAX(score_date)
                          FROM risk_scores
                          WHERE patient_id = p.id
                      )
                    ORDER BY rs.score DESC, p.id
                    """
                )
                rows = cur.fetchall()

      print("\nPatients and latest risk band:")
      for r in rows:
                risk = f"{r['score']:.2f}" if r["score"] is not None else "N/A"
                band = r["risk_band"] or "N/A"
                smoker = "yes" if r["smoker"] else "no"
                print(
                    f"- [{r['id']}] {r['name']} (ext={r['external_id']}, "
                    f"smoker={smoker}) -> risk={risk} ({band}) on {r['score_date']}"
                )

  def show_patient_timeline(patient_id: int):
        with get_connection() as conn:
                  cur = conn.cursor()

            cur.execute("SELECT name FROM patients WHERE id = ?", (patient_id,))
        p = cur.fetchone()
        if not p:
                      print(f"No patient with id={patient_id}")
                      return
                  name = p["name"]

        cur.execute(
                      """
                                  SELECT id, visit_date, reason, notes
                                              FROM visits
                                                          WHERE patient_id = ?
                                                                      ORDER BY visit_date
                                                                                  """,
                      (patient_id,),
        )
        visits = cur.fetchall()

        print(f"\nVisit timeline for {name} (id={patient_id}):")
        for v in visits:
                      print(f"Visit {v['id']} on {v['visit_date']}: {v['reason']}")
                      cur.execute(
                          """
                          SELECT test_name, value, unit, measured_at
                          FROM lab_results
                          WHERE visit_id = ?
                          ORDER BY measured_at
                          """,
                          (v["id"],),
                      )
                      labs = cur.fetchall()
                      for lab in labs:
                                        print(
                                                              f"  - {lab['test_name']}: {lab['value']} "
                                                              f"{lab['unit']} on {lab['measured_at']}"
                                        )

          def list_open_alerts():
                with get_connection() as conn:
                          cur = conn.cursor()
                          cur.execute(
                              """
                              SELECT a.id, a.patient_id, p.name, a.alert_type, a.message, a.created_at
                              FROM alerts a
                              JOIN patients p ON p.id = a.patient_id
                              WHERE a.acknowledged = 0
                              ORDER BY a.created_at DESC
                              """
                          )
                          rows = cur.fetchall()

                print("\nOpen alerts:")
                if not rows:
                          print("No open alerts.")
                          return

                for r in rows:
                          print(
                                        f"- Alert {r['id']} for {r['name']} (pid={r['patient_id']}): "
                                        f"{r['alert_type']} – {r['message']} [{r['created_at']}]"
                          )

            if __name__ == "__main__":
                  list_patients_with_latest_risk()
                  show_patient_timeline(1)
                  list_open_alerts()

# seed_and_score.py
from datetime import date
from db import get_connection

def seed_reference_data(conn):
    cur = conn.cursor()

    conditions = [
        ("T2DM", "Type 2 Diabetes Mellitus"),
        ("HTN", "Hypertension"),
        ("CKD", "Chronic Kidney Disease"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO conditions (code, description) VALUES (?, ?)",
        conditions,
    )

    clinicians = [
        ("Dr. Sen", "Endocrinology", "dr.sen@example.com"),
        ("Dr. Roy", "Cardiology", "dr.roy@example.com"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO clinicians (name, specialty, email) VALUES (?, ?, ?)",
        clinicians,
    )

def seed_patients_and_visits(conn):
    cur = conn.cursor()

    patients = [
        ("EXT001", "Anupam Das", "1980-02-15", "M", 1),
        ("EXT002", "Meera Pal", "1972-09-01", "F", 0),
        ("EXT003", "Rakesh Ghosh", "1990-11-30", "M", 1),
    ]
    cur.executemany(
        """
        INSERT OR IGNORE INTO patients
        (external_id, name, date_of_birth, sex, smoker)
        VALUES (?, ?, ?, ?, ?)
        """,
        patients,
    )

    cur.execute("SELECT id, code FROM conditions")
    cond_map = {row["code"]: row["id"] for row in cur.fetchall()}

    patient_conditions = [
        ("EXT001", "T2DM"),
        ("EXT001", "HTN"),
        ("EXT002", "HTN"),
        ("EXT003", "T2DM"),
    ]
    for ext_id, code in patient_conditions:
        cur.execute("SELECT id FROM patients WHERE external_id = ?", (ext_id,))
        patient = cur.fetchone()
        if not patient:
            continue
        pid = patient["id"]
        cid = cond_map[code]
        cur.execute(
            """
            INSERT OR IGNORE INTO patient_conditions
            (patient_id, condition_id, diagnosed_on)
            VALUES (?, ?, ?)
            """,
            (pid, cid, "2020-01-01"),
        )

    cur.execute("SELECT id FROM clinicians ORDER BY id")
    clinician_ids = [row["id"] for row in cur.fetchall()]

    cur.execute("SELECT id, external_id FROM patients ORDER BY id")
    p_rows = cur.fetchall()
    visits = []
    for i, prow in enumerate(p_rows):
        pid = prow["id"]
        visits.append(
            (pid, clinician_ids[i % len(clinician_ids)],
             "2025-01-05", "Follow-up", "Routine check")
        )
        visits.append(
            (pid, clinician_ids[(i + 1) % len(clinician_ids)],
             "2025-04-10", "Lab follow-up", "Dose adjustment")
        )

    cur.executemany(
        """
        INSERT INTO visits (patient_id, clinician_id, visit_date, reason, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        visits,
    )

    cur.execute("SELECT id, visit_date FROM visits ORDER BY id")
    visit_rows = cur.fetchall()

    lab_rows = []
    for v in visit_rows:
        vid = v["id"]
        visit_date = v["visit_date"]

        if vid % 2 == 0:
            hba1c = 8.2
            ldl = 160.0
        else:
            hba1c = 6.8
            ldl = 130.0

        lab_rows.extend([
            (vid, "HbA1c", hba1c, "%", 4.0, 6.5, visit_date),
            (vid, "LDL", ldl, "mg/dL", 0.0, 130.0, visit_date),
        ])

    cur.executemany(
        """
        INSERT INTO lab_results
        (visit_id, test_name, value, unit, normal_low, normal_high, measured_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        lab_rows,
    )

def risk_from_rules(smoker: bool, labs, conds):
    """
    Simple rule-based chronic disease burden score in [0, 1],
    combining HbA1c, LDL, chronic conditions, and smoking.
    """
    score = 0.0
    reasons = []

    hba1c = labs.get("HbA1c")
    ldl = labs.get("LDL")

    if hba1c:
        if hba1c["value"] > 9.0:
            score += 0.4
            reasons.append("HbA1c > 9")
        elif hba1c["value"] > 7.5:
            score += 0.25
            reasons.append("HbA1c > 7.5")
        elif hba1c["value"] > 6.5:
            score += 0.1
            reasons.append("HbA1c mildly elevated")

    if ldl:
        if ldl["value"] > 190:
            score += 0.4
            reasons.append("LDL > 190")
        elif ldl["value"] > 160:
            score += 0.25
            reasons.append("LDL > 160")
        elif ldl["value"] > 130:
            score += 0.1
            reasons.append("LDL > 130")

    if "T2DM" in conds:
        score += 0.15
        reasons.append("T2DM diagnosis")

    if "HTN" in conds:
        score += 0.1
        reasons.append("Hypertension diagnosis")

    if smoker:
        score += 0.1
        reasons.append("Current smoker")

    score = min(score, 1.0)

    if score >= 0.6:
        band = "HIGH"
    elif score >= 0.3:
        band = "MODERATE"
    else:
        band = "LOW"

    explanation = "; ".join(reasons) if reasons else "No major risk factors"
    return score, band, explanation

def create_alerts_for_patient(cur, patient_id, band, labs):
    messages = []

    if band == "HIGH":
        messages.append("Overall risk band HIGH – consider closer follow-up.")

    hba1c = labs.get("HbA1c")
    if hba1c and hba1c["value"] > 9.0:
        messages.append(f"HbA1c extremely high ({hba1c['value']}%).")

    ldl = labs.get("LDL")
    if ldl and ldl["value"] > 190.0:
        messages.append(f"LDL extremely high ({ldl['value']} mg/dL).")

    for msg in messages:
        cur.execute(
            """
            INSERT INTO alerts (patient_id, alert_type, message)
            VALUES (?, ?, ?)
            """,
            (patient_id, "RISK_SPIKE", msg),
        )

def compute_risk_for_all_patients(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, external_id, name, smoker FROM patients")
    patients = cur.fetchall()

    for p in patients:
        pid = p["id"]

        cur.execute(
            """
            SELECT l.test_name, l.value, l.normal_low, l.normal_high
            FROM lab_results l
            JOIN visits v ON l.visit_id = v.id
            WHERE v.patient_id = ?
            ORDER BY l.measured_at DESC
            """,
            (pid,),
        )
        lab_rows = cur.fetchall()
        labs = {row["test_name"]: row for row in lab_rows}

        cur.execute(
            """
            SELECT c.code
            FROM patient_conditions pc
            JOIN conditions c ON pc.condition_id = c.id
            WHERE pc.patient_id = ?
            """,
            (pid,),
        )
        cond_codes = {row["code"] for row in cur.fetchall()}

        risk_score, band, explanation = risk_from_rules(
            smoker=bool(p["smoker"]),
            labs=labs,
            conds=cond_codes,
        )

        today = date.today().isoformat()
        cur.execute(
            """
            INSERT INTO risk_scores (patient_id, score_date, score, risk_band, explanation)
            VALUES (?, ?, ?, ?, ?)
            """,
            (pid, today, risk_score, band, explanation),
        )

        create_alerts_for_patient(cur, pid, band, labs)

def main():
    with get_connection() as conn:
        seed_reference_data(conn)
        seed_patients_and_visits(conn)
        compute_risk_for_all_patients(conn)
    print("Seeded data and computed risk scores.")

if __name__ == "__main__":
    main()

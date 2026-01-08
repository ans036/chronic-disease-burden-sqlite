# Chronic Disease Burden – SQLite + Python

This repository contains a small but realistic SQLite schema and Python tooling for chronic disease burden tracking. It is modeled after the patient, lab, and risk-score data I worked with during my Machine Learning Internship at Doyen Diagnostics, where I built an end-to-end ML pipeline that improved disease-burden prediction by 15%.

In that internship, I used a semi-supervised DNN with label propagation and a Gaussian kernel to achieve robust health-score modeling from only 78 labeled samples. The model sat downstream of a structured data layer that looked a lot like this one: patients with chronic conditions, longitudinal lab values, and derived risk scores over time. This project isolates that data layer in a standalone SQLite database and shows how patient information can be organized and queried before being exported into an ML pipeline.

## Schema at a glance

- `patients` – Demographics and smoking status, keyed by an external LIS/EMR identifier.
- `clinicians` – Doctors and their specialties.
- `conditions` / `patient_conditions` – Chronic conditions (for example, T2DM, HTN, CKD) associated with each patient.
- `visits` – Longitudinal visits with dates, reasons, and notes.
- `lab_results` – Key lab tests (for example, HbA1c, LDL) per visit, with normal ranges.
- `risk_scores` – Simple rule-based chronic disease burden scores in \[0, 1\], with LOW / MODERATE / HIGH bands and an explanation string.
- `alerts` – Flags when overall risk is high or when critical labs are severely out of range.

This mirrors the kind of schema you would expect in a lightweight chronic-disease registry or analytics layer on top of an EHR.

## Files

- `schema.sql` – SQLite schema and indexes for patients, clinicians, conditions, visits, lab_results, risk_scores, and alerts.
- `db.py` – Small helper for opening SQLite connections with foreign keys enabled.
- `init_db.py` – Creates `chronic_disease.db` from `schema.sql`.
- `seed_and_score.py` – Inserts sample patients, visits, and lab measurements, then computes a transparent rule-based disease-burden score and raises alerts when thresholds are crossed.
- `reports.py` – Example read-side queries and reports:
  - Latest risk score per patient.
  - Visit and lab timeline for a given patient.
  - List of open (unacknowledged) alerts.
- `requirements.txt` – Listed for completeness; the project only relies on the Python standard library (`sqlite3`).

## How to run

```bash
   # 1. Initialize the database
   python init_db.py

   # 2. Seed sample data and compute risk scores
   python seed_and_score.py

   # 3. Run example reports
   python reports.py
```

## Contact

For questions or suggestions, please email ani.tubai022@gmail.com or open an issue on the GitHub repository.
              

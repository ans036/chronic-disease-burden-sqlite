# Chronic Disease Burden – SQLite + Python

This repository contains a small but realistic SQLite schema and Python tooling for chronic disease burden tracking. It is modeled after the kind of patient, lab, and risk-score data I worked with during my Machine Learning Internship at Doyen Diagnostics, where I built an end-to-end ML pipeline for disease-burden prediction and health-score modeling.

Here the focus is purely on the **data layer**: how patient information, visits, lab results, and derived risk scores can be stored and queried in a clean relational schema before being exported into a machine learning pipeline.

## Schema at a glance

- **patients** – demographics and smoking status.
- - **clinicians** – doctors and specialties.
- - **conditions / patient_conditions** – chronic diseases per patient.
- - **visits** – longitudinal visits with reasons and notes.
- - **lab_results** – key lab tests (e.g., HbA1c, LDL) per visit.
- - **risk_scores** – simple rule-based chronic disease burden scores (0–1, with LOW/MODERATE/HIGH bands).
- - **alerts** – flags when risk is high or labs are critically abnormal.
           
- ## Usage
           
- ```bash
  python init_db.py          # create chronic_disease.db from schema.sql
  python seed_and_score.py   # insert sample data and compute risk_scores + alerts
  python reports.py          # run example reports on the command line
  ```

In a real ML workflow this database would sit upstream of the modeling code: data would be pulled from patients, patient_conditions, lab_results, and risk_scores into a pandas DataFrame and then used to train and evaluate disease-burden models.

## Contact

For questions or suggestions, please email ani.tubai022@gmail.com or open an issue on the GitHub repository.
              

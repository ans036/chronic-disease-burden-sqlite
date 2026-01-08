-- schema.sql
-- Chronic disease burden tracking database

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS patients (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      external_id TEXT UNIQUE,              -- ID from LIS / EMR
    name TEXT NOT NULL,
      date_of_birth TEXT NOT NULL,          -- YYYY-MM-DD
    sex TEXT CHECK (sex IN ('M', 'F', 'O')) DEFAULT 'O',
      smoker INTEGER DEFAULT 0,             -- 0/1
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
  );

CREATE TABLE IF NOT EXISTS clinicians (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      specialty TEXT,
      email TEXT UNIQUE,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
  );

CREATE TABLE IF NOT EXISTS conditions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      code TEXT UNIQUE NOT NULL,            -- e.g. "T2DM", "HTN"
    description TEXT NOT NULL
  );

CREATE TABLE IF NOT EXISTS patient_conditions (
      patient_id INTEGER NOT NULL,
      condition_id INTEGER NOT NULL,
      diagnosed_on TEXT NOT NULL,           -- YYYY-MM-DD
    PRIMARY KEY (patient_id, condition_id),
      FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
      FOREIGN KEY (condition_id) REFERENCES conditions(id) ON DELETE CASCADE
  );

CREATE TABLE IF NOT EXISTS visits (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      patient_id INTEGER NOT NULL,
      clinician_id INTEGER,
      visit_date TEXT NOT NULL,
      reason TEXT,
      notes TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
      FOREIGN KEY (clinician_id) REFERENCES clinicians(id) ON DELETE SET NULL
  );

CREATE TABLE IF NOT EXISTS lab_results (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      visit_id INTEGER NOT NULL,
      test_name TEXT NOT NULL,              -- e.g. "HbA1c", "LDL"
    value REAL NOT NULL,
      unit TEXT NOT NULL,
      normal_low REAL,
      normal_high REAL,
      measured_at TEXT NOT NULL,            -- YYYY-MM-DD
    FOREIGN KEY (visit_id) REFERENCES visits(id) ON DELETE CASCADE
  );

-- Risk scores computed from labs + conditions
CREATE TABLE IF NOT EXISTS risk_scores (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      patient_id INTEGER NOT NULL,
      score_date TEXT NOT NULL,
      score REAL NOT NULL,                  -- 0–1 scaled disease-burden risk
    risk_band TEXT NOT NULL,              -- "LOW", "MODERATE", "HIGH"
    explanation TEXT,                     -- human-readable rule hits
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
  );

-- Alerts raised when risk crosses threshold or labs are very abnormal
CREATE TABLE IF NOT EXISTS alerts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      patient_id INTEGER NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      alert_type TEXT NOT NULL,             -- "LAB_ABNORMAL", "RISK_SPIKE"
    message TEXT NOT NULL,
      acknowledged INTEGER DEFAULT 0,
      FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
  );

CREATE INDEX IF NOT EXISTS idx_visits_patient_date
    ON visits(patient_id, visit_date);

CREATE INDEX IF NOT EXISTS idx_labs_visit_test
    ON lab_results(visit_id, test_name);

CREATE INDEX IF NOT EXISTS idx_risk_scores_patient_date
    ON risk_scores(patient_id, score_date);

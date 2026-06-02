# 🛡️ Counter Fraud – Data Quality & Analytics System
### SAMA-Aligned | Saudi Digital Banking | Fraud Risk Analytics

<p align="center">
  <a href="https://fraud-analytics-platform-sovwrvwsyapfzhbrbqyaev.streamlit.app/" target="_blank">
    <img src="https://img.shields.io/badge/🚀%20Live%20Dashboard-Click%20to%20View-red?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Dashboard"/>
  </a>
  &nbsp;
  <img src="https://img.shields.io/badge/SAMA-Compliant-green?style=for-the-badge" alt="SAMA"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  &nbsp;
  <img src="https://img.shields.io/badge/SQL-Advanced-orange?style=for-the-badge&logo=postgresql&logoColor=white" alt="SQL"/>
</p>

<p align="center">
  <b>👉 <a href="https://fraud-analytics-platform-sovwrvwsyapfzhbrbqyaev.streamlit.app/">Click here to open the Live Interactive Dashboard</a> 👈</b>
</p>

---

> **Built as a portfolio project aligned with the Counter Fraud – Data Quality Specialist role at Atmaal, Riyadh.**
> Demonstrates end-to-end fraud data quality management, analytics, anomaly detection, and SAMA-compliant regulatory reporting.

---

## 📌 Project Overview

This project simulates a **production-grade Fraud Data Quality & Analytics System** for a Saudi digital bank operating under SAMA (Saudi Arabian Monetary Authority) Counter Fraud guidelines.

It covers every responsibility listed in the job description:

| JD Requirement | Project Coverage |
|---|---|
| Fraud data validation, deduplication, completeness | `sql/01_data_quality_checks.sql` + `python/fraud_dq_analysis.py` |
| Fraud detection analytics, anomaly detection | Z-Score engine, trend analytics in Python |
| Fraud data frameworks and data flows | Documented data pipeline (raw → clean → report) |
| Regulatory fraud reporting (SAMA) | Dashboard page + monthly reporting table |
| Rule tuning & scenario testing | SQL: high-risk thresholds, risk score validation |
| Cross-functional fraud data governance | Documented scorecard + DQ framework |

---

## 🗂️ Project Structure

```text
fraud_dq_project/
│
├── data/
│   ├── generate_data.py              # Synthetic 50K fraud transaction generator
│   ├── fraud_transactions_raw.csv    # Raw dataset (with injected DQ issues)
│   ├── fraud_transactions_clean.csv  # Deduplicated, validated dataset
│   ├── anomalies.csv                 # Z-score flagged anomalous transactions
│   ├── monthly_summary.csv           # Monthly fraud trend data
│   ├── fraud_by_type.csv             # Fraud typology breakdown
│   ├── channel_stats.csv             # Fraud by channel
│   └── mule_candidates.csv           # High-risk customer flags
│
├── sql/
│   └── 01_data_quality_checks.sql    # 6-section SQL DQ suite (50+ queries)
│
├── python/
│   └── fraud_dq_analysis.py          # Full DQ + fraud analytics engine
│
├── dashboard/
│   └── app.py                        # Streamlit interactive dashboard
│
└── report/
    └── dq_scorecard.json             # Machine-readable DQ scorecard output
```

---

## 📊 Dataset Summary

- **50,000** synthetic banking transactions (2024 full year)
- Saudi cities: Riyadh, Jeddah, Dammam, Mecca, Medina +
- Channels: Mobile App, Web, ATM, Branch, IVR
- **~3.5% fraud rate** (realistic for digital banking)
- Fraud typologies: Account Takeover, Card-Not-Present, Identity Theft, Mule Account, Phishing
- **Injected DQ issues:** 499 duplicate transaction IDs, 800 null account numbers, 1,000 null merchant categories, 1,957 null IP addresses

---

## 🔍 Data Quality Checks (SQL + Python)

### 1. Completeness Checks
- Field-level null audit across all 16 columns
- Critical field check: fraud records missing account/IP/device data
- Severity classification (HIGH / MEDIUM / INFO)

### 2. Deduplication
- Exact duplicate detection on `transaction_id`
- Near-duplicate detection: same customer + amount within 60 seconds
- **Found:** 499 duplicates (1.0% of dataset) → deduplicated before analysis

### 3. Validity Checks
- Amount validation (≤ 0 SAR flagged)
- Future-dated transaction detection
- Enum validation for transaction status
- Risk score range validation [0–100]

### 4. Consistency Checks
- Fraud flag with no fraud type → data inconsistency
- Non-fraud records with risk score ≥ 80 → potential misclassification (9,561 found)
- SAMA reporting consistency: **430 fraud cases unreported** (SAR 939,088)

---

## 📡 Anomaly Detection

**Method:** Z-Score statistical anomaly detection on completed transaction amounts

- Mean transaction: SAR 2,477
- Std deviation: SAR 19,945
- **94 anomalous transactions** (|Z| > 3σ) flagged
- 7.4% fraud rate among anomalies vs 3.5% baseline → **2x fraud enrichment**
- Total anomaly value: SAR 27.9M

---

## 🚨 Fraud Analytics

| Metric | Value |
|---|---|
| Total fraud cases | 1,732 |
| Fraud rate | 3.5% |
| Top fraud type | Card-Not-Present (374 cases) |
| Highest value type | Identity Theft (SAR 1.3M) |
| Highest risk channel | ATM (3.80% fraud rate) |
| Mule account candidates | 192 customers |
| Unreported to SAMA | 430 cases / SAR 939K |

---

## 🏦 SAMA Regulatory Alignment

This system is designed to support compliance with **SAMA's Cyber Security Framework** and **Counter Fraud reporting requirements**:

- Monthly fraud reporting by volume and value
- Fraud typology categorization per SAMA taxonomy
- 72-hour reporting window monitoring
- Unreported fraud alerts with case + value summary
- Data quality score for audit trail

---

## 🛠️ Tech Stack

| Tool | Usage |
|---|---|
| Python + Pandas | Data generation, DQ analysis, anomaly detection |
| NumPy | Z-score statistical analysis |
| SQL (PostgreSQL-compatible) | 6-section DQ query suite |
| Streamlit | Interactive dashboard framework |
| Plotly | Data visualization |
| JSON | Machine-readable scorecard output |

---

## ▶️ How to Run

```bash
# 1. Install dependencies
pip install pandas numpy streamlit plotly

# 2. Generate dataset
python data/generate_data.py

# 3. Run analysis engine
python python/fraud_dq_analysis.py

# 4. Launch dashboard
streamlit run dashboard/app.py
```

---

## 👤 Author

**Gayasuddin**  
Data Analyst | Fraud Risk & Data Quality  
📧 mohdfayaz7017052276@gmail.com  
🔗 linkedin.com/in/gayasuddin

---

*This project was built to demonstrate practical fraud data quality skills aligned with the Counter Fraud – Data Quality Specialist role at Atmaal, Riyadh, Saudi Arabia.*

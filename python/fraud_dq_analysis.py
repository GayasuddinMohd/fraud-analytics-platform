"""
Counter Fraud – Data Quality & Analytics Engine
Author: Gayasuddin | SAMA-Aligned Fraud Data Quality Project
Tools: Python, Pandas, NumPy
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

print("=" * 65)
print("  COUNTER FRAUD – DATA QUALITY ANALYSIS ENGINE")
print("  SAMA-Aligned | Digital Banking Fraud Detection")
print("=" * 65)

# ── Load Data ────────────────────────────────────────────────
df = pd.read_csv('data/fraud_transactions_raw.csv', parse_dates=['transaction_date'])
print(f"\n[DATA LOADED] {len(df):,} transactions | Period: {df['transaction_date'].min().date()} → {df['transaction_date'].max().date()}")

# ── 1. COMPLETENESS ANALYSIS ─────────────────────────────────
print("\n" + "─" * 50)
print("  SECTION 1: COMPLETENESS CHECKS")
print("─" * 50)

null_summary = df.isnull().sum().reset_index()
null_summary.columns = ['field', 'null_count']
null_summary['null_pct'] = (null_summary['null_count'] / len(df) * 100).round(2)
null_summary = null_summary[null_summary['null_count'] > 0].sort_values('null_pct', ascending=False)

print("\nFields with missing values:")
print(null_summary.to_string(index=False))

# Critical fields (fraud records)
fraud_df = df[df['is_fraud'] == 1].copy()
critical_nulls = fraud_df[['transaction_id', 'account_number', 'merchant_category', 'ip_address', 'device_id']].isnull().any(axis=1).sum()
print(f"\n⚠  Fraud records with at least one critical field missing: {critical_nulls} ({critical_nulls/len(fraud_df)*100:.1f}%)")

# ── 2. DEDUPLICATION ─────────────────────────────────────────
print("\n" + "─" * 50)
print("  SECTION 2: DEDUPLICATION")
print("─" * 50)

total = len(df)
duplicates = df.duplicated(subset='transaction_id', keep='first').sum()
dup_pct = duplicates / total * 100

print(f"\nTotal records       : {total:,}")
print(f"Unique transactions : {df['transaction_id'].nunique():,}")
print(f"Duplicate records   : {duplicates:,} ({dup_pct:.2f}%)")

# Near-duplicates: same customer + amount within 60 seconds
df_sorted = df.sort_values(['customer_id', 'amount_sar', 'transaction_date'])
df_sorted['prev_customer'] = df_sorted['customer_id'].shift(1)
df_sorted['prev_amount']   = df_sorted['amount_sar'].shift(1)
df_sorted['prev_date']     = df_sorted['transaction_date'].shift(1)
df_sorted['time_diff_sec'] = (df_sorted['transaction_date'] - df_sorted['prev_date']).dt.total_seconds().abs()

near_dups = df_sorted[
    (df_sorted['customer_id'] == df_sorted['prev_customer']) &
    (df_sorted['amount_sar']  == df_sorted['prev_amount']) &
    (df_sorted['time_diff_sec'] < 60)
]
print(f"Near-duplicate pairs (same customer+amount <60s): {len(near_dups):,}")

# Clean deduplicated dataframe
df_dedup = df.drop_duplicates(subset='transaction_id', keep='first').copy()
print(f"\nAfter deduplication : {len(df_dedup):,} records retained")

# ── 3. VALIDITY CHECKS ───────────────────────────────────────
print("\n" + "─" * 50)
print("  SECTION 3: VALIDITY CHECKS")
print("─" * 50)

invalid_amounts   = df_dedup[df_dedup['amount_sar'] <= 0]
future_dates      = df_dedup[df_dedup['transaction_date'] > datetime.now()]
invalid_status    = df_dedup[~df_dedup['transaction_status'].isin(['COMPLETED','FAILED','REVERSED','PENDING'])]
invalid_risk      = df_dedup[(df_dedup['risk_score'] < 0) | (df_dedup['risk_score'] > 100)]

print(f"\nInvalid amounts (≤0 SAR)          : {len(invalid_amounts):,}")
print(f"Future-dated transactions          : {len(future_dates):,}")
print(f"Invalid transaction status values  : {len(invalid_status):,}")
print(f"Risk score out of range [0–100]    : {len(invalid_risk):,}")

# ── 4. CONSISTENCY CHECKS ────────────────────────────────────
print("\n" + "─" * 50)
print("  SECTION 4: CONSISTENCY CHECKS")
print("─" * 50)

fraud_no_type     = df_dedup[(df_dedup['is_fraud'] == 1) & (df_dedup['fraud_type'].isna())]
false_negative    = df_dedup[(df_dedup['is_fraud'] == 0) & (df_dedup['risk_score'] >= 80)]
unreported_sama   = df_dedup[(df_dedup['is_fraud'] == 1) & (df_dedup['reported_to_sama'] == 0)]

print(f"\nFraud records with no fraud_type   : {len(fraud_no_type):,}  ← Data inconsistency")
print(f"Non-fraud with risk_score ≥ 80     : {len(false_negative):,}  ← Potential misclassification")
print(f"Fraud not reported to SAMA         : {len(unreported_sama):,}  ← Regulatory gap ⚠")
print(f"  └─ Unreported value (SAR)        : {unreported_sama['amount_sar'].sum():,.2f}")

# ── 5. Z-SCORE ANOMALY DETECTION ─────────────────────────────
print("\n" + "─" * 50)
print("  SECTION 5: ANOMALY DETECTION (Z-Score)")
print("─" * 50)

completed = df_dedup[df_dedup['transaction_status'] == 'COMPLETED'].copy()
mean_amt  = completed['amount_sar'].mean()
std_amt   = completed['amount_sar'].std()
completed['z_score'] = (completed['amount_sar'] - mean_amt) / std_amt

anomalies = completed[completed['z_score'].abs() > 3].sort_values('z_score', ascending=False)
print(f"\nMean transaction amount  : SAR {mean_amt:,.2f}")
print(f"Std deviation            : SAR {std_amt:,.2f}")
print(f"Anomalous records (|Z|>3): {len(anomalies):,}")
print(f"  └─ Fraud among anomalies: {anomalies['is_fraud'].sum():,} ({anomalies['is_fraud'].mean()*100:.1f}%)")
print(f"  └─ Total anomaly value  : SAR {anomalies['amount_sar'].sum():,.2f}")

# ── 6. FRAUD TREND ANALYTICS ─────────────────────────────────
print("\n" + "─" * 50)
print("  SECTION 6: FRAUD TREND ANALYTICS")
print("─" * 50)

df_dedup['month'] = df_dedup['transaction_date'].dt.to_period('M')

monthly = df_dedup.groupby('month').agg(
    total_txns   = ('transaction_id', 'count'),
    fraud_count  = ('is_fraud', 'sum'),
    fraud_value  = ('amount_sar', lambda x: x[df_dedup.loc[x.index, 'is_fraud'] == 1].sum())
).reset_index()
monthly['fraud_rate'] = (monthly['fraud_count'] / monthly['total_txns'] * 100).round(3)

print("\nMonthly Fraud Summary:")
print(monthly.to_string(index=False))

# By fraud type
fraud_by_type = fraud_df.groupby('fraud_type').agg(
    cases       = ('transaction_id', 'count'),
    total_value = ('amount_sar', 'sum'),
    avg_value   = ('amount_sar', 'mean')
).reset_index().sort_values('cases', ascending=False)
print("\nFraud by Typology:")
print(fraud_by_type.to_string(index=False))

# By channel
channel_stats = df_dedup.groupby('channel').agg(
    total  = ('transaction_id', 'count'),
    fraud  = ('is_fraud', 'sum')
).reset_index()
channel_stats['fraud_rate'] = (channel_stats['fraud'] / channel_stats['total'] * 100).round(3)
channel_stats = channel_stats.sort_values('fraud_rate', ascending=False)
print("\nFraud by Channel:")
print(channel_stats.to_string(index=False))

# ── 7. MULE ACCOUNT DETECTION ────────────────────────────────
print("\n" + "─" * 50)
print("  SECTION 7: HIGH-RISK CUSTOMER FLAGGING")
print("─" * 50)

mule_candidates = fraud_df.groupby('customer_id').agg(
    fraud_count     = ('transaction_id', 'count'),
    total_amount    = ('amount_sar', 'sum'),
    max_risk_score  = ('risk_score', 'max')
).reset_index()
mule_candidates = mule_candidates[mule_candidates['fraud_count'] >= 2].sort_values('fraud_count', ascending=False)
print(f"\nCustomers with ≥2 fraud events (Mule Account Candidates): {len(mule_candidates):,}")
print(mule_candidates.head(10).to_string(index=False))

# ── 8. DQ SCORECARD ──────────────────────────────────────────
print("\n" + "═" * 65)
print("  DATA QUALITY SCORECARD – EXECUTIVE SUMMARY")
print("═" * 65)

issues = duplicates + len(fraud_no_type) + invalid_amounts.shape[0] + len(unreported_sama)
dq_score = max(0, round((len(df) - issues) / len(df) * 100, 1))

scorecard = {
    "report_date"           : datetime.now().strftime("%Y-%m-%d"),
    "total_records"         : int(total),
    "unique_transactions"   : int(df['transaction_id'].nunique()),
    "duplicate_records"     : int(duplicates),
    "duplicate_rate_pct"    : round(dup_pct, 2),
    "null_account_numbers"  : int(df['account_number'].isna().sum()),
    "null_merchant_ids"     : int(df['merchant_category'].isna().sum()),
    "invalid_amounts"       : int(len(invalid_amounts)),
    "inconsistent_fraud"    : int(len(fraud_no_type)),
    "unreported_to_sama"    : int(len(unreported_sama)),
    "anomalous_transactions": int(len(anomalies)),
    "mule_account_flags"    : int(len(mule_candidates)),
    "overall_dq_score_pct"  : dq_score
}

for k, v in scorecard.items():
    print(f"  {k:<30}: {v}")

os.makedirs('report', exist_ok=True)
with open('report/dq_scorecard.json', 'w') as f:
    json.dump(scorecard, f, indent=2)

# Save processed data for dashboard
df_dedup['z_score'] = np.where(
    df_dedup['transaction_status'] == 'COMPLETED',
    (df_dedup['amount_sar'] - mean_amt) / std_amt,
    np.nan
)
df_dedup.to_csv('data/fraud_transactions_clean.csv', index=False)
anomalies[['transaction_id','customer_id','amount_sar','z_score','is_fraud','channel','city','transaction_date']].to_csv('data/anomalies.csv', index=False)
monthly.to_csv('data/monthly_summary.csv', index=False)
fraud_by_type.to_csv('data/fraud_by_type.csv', index=False)
channel_stats.to_csv('data/channel_stats.csv', index=False)
mule_candidates.to_csv('data/mule_candidates.csv', index=False)

print("\n✓ Analysis complete. Output files saved to /data and /report")

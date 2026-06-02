-- ============================================================
-- COUNTER FRAUD – DATA QUALITY CHECKS
-- Author: Gayasuddin | SAMA-Aligned Fraud Data Quality Project
-- Description: Comprehensive DQ validation suite for fraud
--              transaction data in a Saudi digital banking context
-- ============================================================

-- ============================================================
-- 1. COMPLETENESS CHECKS
-- Check for NULL/missing values in critical fraud data fields
-- ============================================================

-- 1a. Overall completeness scorecard
SELECT
    'transaction_id'    AS field_name, COUNT(*) - COUNT(transaction_id)    AS null_count, ROUND((COUNT(*) - COUNT(transaction_id))  * 100.0 / COUNT(*), 2) AS null_pct FROM fraud_transactions
UNION ALL
SELECT 'customer_id',      COUNT(*) - COUNT(customer_id),      ROUND((COUNT(*) - COUNT(customer_id))      * 100.0 / COUNT(*), 2) FROM fraud_transactions
UNION ALL
SELECT 'account_number',   COUNT(*) - COUNT(account_number),   ROUND((COUNT(*) - COUNT(account_number))   * 100.0 / COUNT(*), 2) FROM fraud_transactions
UNION ALL
SELECT 'transaction_date', COUNT(*) - COUNT(transaction_date), ROUND((COUNT(*) - COUNT(transaction_date)) * 100.0 / COUNT(*), 2) FROM fraud_transactions
UNION ALL
SELECT 'amount_sar',       COUNT(*) - COUNT(amount_sar),       ROUND((COUNT(*) - COUNT(amount_sar))       * 100.0 / COUNT(*), 2) FROM fraud_transactions
UNION ALL
SELECT 'merchant_id',      COUNT(*) - COUNT(merchant_id),      ROUND((COUNT(*) - COUNT(merchant_id))      * 100.0 / COUNT(*), 2) FROM fraud_transactions
UNION ALL
SELECT 'device_id',        COUNT(*) - COUNT(device_id),        ROUND((COUNT(*) - COUNT(device_id))        * 100.0 / COUNT(*), 2) FROM fraud_transactions
UNION ALL
SELECT 'ip_address',       COUNT(*) - COUNT(ip_address),       ROUND((COUNT(*) - COUNT(ip_address))       * 100.0 / COUNT(*), 2) FROM fraud_transactions
ORDER BY null_pct DESC;

-- 1b. Fraud records with missing critical fields (HIGH RISK)
-- Fraud cases missing regulatory-required fields need immediate escalation
SELECT
    transaction_id,
    customer_id,
    fraud_type,
    amount_sar,
    CASE WHEN account_number IS NULL THEN 'MISSING' ELSE 'OK' END AS account_status,
    CASE WHEN merchant_id   IS NULL THEN 'MISSING' ELSE 'OK' END AS merchant_status,
    CASE WHEN ip_address    IS NULL THEN 'MISSING' ELSE 'OK' END AS ip_status,
    CASE WHEN device_id     IS NULL THEN 'MISSING' ELSE 'OK' END AS device_status
FROM fraud_transactions
WHERE is_fraud = 1
  AND (account_number IS NULL OR merchant_id IS NULL OR ip_address IS NULL OR device_id IS NULL)
ORDER BY amount_sar DESC;


-- ============================================================
-- 2. DEDUPLICATION CHECKS
-- Identify duplicate transaction records that inflate fraud counts
-- ============================================================

-- 2a. Find duplicate transaction IDs
SELECT
    transaction_id,
    COUNT(*) AS occurrence_count,
    MIN(transaction_date) AS first_seen,
    MAX(transaction_date) AS last_seen,
    SUM(amount_sar)       AS total_amount,
    MAX(CASE WHEN is_fraud = 1 THEN 'YES' ELSE 'NO' END) AS any_fraud_flag
FROM fraud_transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC;

-- 2b. Deduplication summary
SELECT
    COUNT(*)                                        AS total_records,
    COUNT(DISTINCT transaction_id)                  AS unique_transactions,
    COUNT(*) - COUNT(DISTINCT transaction_id)       AS duplicate_records,
    ROUND((COUNT(*) - COUNT(DISTINCT transaction_id)) * 100.0 / COUNT(*), 2) AS duplicate_pct
FROM fraud_transactions;

-- 2c. Suspected same-transaction duplicates (same customer, amount, date within 60 seconds)
SELECT
    a.transaction_id    AS tx_id_1,
    b.transaction_id    AS tx_id_2,
    a.customer_id,
    a.amount_sar,
    a.transaction_date  AS time_1,
    b.transaction_date  AS time_2,
    ABS(EXTRACT(EPOCH FROM (b.transaction_date - a.transaction_date))) AS seconds_apart
FROM fraud_transactions a
JOIN fraud_transactions b
  ON  a.customer_id     = b.customer_id
  AND a.amount_sar      = b.amount_sar
  AND a.transaction_id <> b.transaction_id
  AND ABS(EXTRACT(EPOCH FROM (b.transaction_date - a.transaction_date))) < 60
ORDER BY seconds_apart;


-- ============================================================
-- 3. VALIDITY CHECKS
-- Ensure data values are within expected domain ranges
-- ============================================================

-- 3a. Invalid amount values
SELECT
    transaction_id, customer_id, amount_sar, transaction_type, transaction_date
FROM fraud_transactions
WHERE amount_sar <= 0
   OR amount_sar IS NULL
   OR amount_sar > 1000000  -- SAR 1M threshold per SAMA guidelines
ORDER BY amount_sar DESC;

-- 3b. Invalid transaction status values
SELECT
    transaction_status,
    COUNT(*) AS count
FROM fraud_transactions
WHERE transaction_status NOT IN ('COMPLETED', 'FAILED', 'REVERSED', 'PENDING')
GROUP BY transaction_status;

-- 3c. Future-dated transactions (data integrity issue)
SELECT
    transaction_id, customer_id, transaction_date, amount_sar
FROM fraud_transactions
WHERE transaction_date > CURRENT_TIMESTAMP
ORDER BY transaction_date;

-- 3d. Risk score out of valid range [0–100]
SELECT COUNT(*) AS invalid_risk_scores
FROM fraud_transactions
WHERE risk_score < 0 OR risk_score > 100;


-- ============================================================
-- 4. CONSISTENCY CHECKS
-- Cross-field logic validation
-- ============================================================

-- 4a. Fraud flagged but no fraud type assigned (inconsistency)
SELECT
    transaction_id, customer_id, is_fraud, fraud_type, amount_sar
FROM fraud_transactions
WHERE is_fraud = 1 AND (fraud_type IS NULL OR fraud_type = '');

-- 4b. Non-fraud records with high risk scores (potential misclassification)
SELECT
    transaction_id, customer_id, risk_score, is_fraud, fraud_type, amount_sar
FROM fraud_transactions
WHERE is_fraud = 0 AND risk_score >= 80
ORDER BY risk_score DESC
LIMIT 50;

-- 4c. SAMA reporting consistency — fraud not reported to SAMA
SELECT
    COUNT(*) AS unreported_fraud_count,
    ROUND(AVG(amount_sar), 2) AS avg_amount,
    SUM(amount_sar)           AS total_unreported_amount
FROM fraud_transactions
WHERE is_fraud = 1 AND (reported_to_sama = 0 OR reported_to_sama IS NULL);


-- ============================================================
-- 5. FRAUD TREND ANALYTICS
-- Advanced analytics for detection and regulatory insight
-- ============================================================

-- 5a. Monthly fraud volume and value (SAMA regulatory format)
SELECT
    DATE_TRUNC('month', transaction_date) AS report_month,
    COUNT(*)                               AS total_transactions,
    SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount_sar ELSE 0 END), 2) AS fraud_value_sar,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 3) AS fraud_rate_pct
FROM fraud_transactions
GROUP BY 1
ORDER BY 1;

-- 5b. Fraud by typology (SAMA fraud category breakdown)
SELECT
    fraud_type,
    COUNT(*)            AS case_count,
    ROUND(SUM(amount_sar), 2) AS total_amount_sar,
    ROUND(AVG(amount_sar), 2) AS avg_amount_sar,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_total_fraud
FROM fraud_transactions
WHERE is_fraud = 1
GROUP BY fraud_type
ORDER BY case_count DESC;

-- 5c. Fraud by channel — where is fraud happening?
SELECT
    channel,
    COUNT(*)            AS total_txns,
    SUM(is_fraud)       AS fraud_cases,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 3) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN is_fraud=1 THEN amount_sar END), 2) AS fraud_value_sar
FROM fraud_transactions
GROUP BY channel
ORDER BY fraud_rate_pct DESC;

-- 5d. High-risk customers — multiple fraud events (mule account detection)
SELECT
    customer_id,
    COUNT(*)            AS total_transactions,
    SUM(is_fraud)       AS fraud_count,
    ROUND(SUM(CASE WHEN is_fraud=1 THEN amount_sar ELSE 0 END), 2) AS total_fraud_amount,
    MAX(risk_score)     AS max_risk_score,
    MIN(transaction_date) AS first_fraud_date,
    MAX(transaction_date) AS last_fraud_date
FROM fraud_transactions
WHERE is_fraud = 1
GROUP BY customer_id
HAVING COUNT(*) >= 2
ORDER BY fraud_count DESC, total_fraud_amount DESC;

-- 5e. Z-Score anomaly detection — statistically unusual transaction amounts
WITH stats AS (
    SELECT
        AVG(amount_sar)    AS mean_amount,
        STDDEV(amount_sar) AS std_amount
    FROM fraud_transactions
    WHERE transaction_status = 'COMPLETED'
),
scored AS (
    SELECT
        t.transaction_id,
        t.customer_id,
        t.amount_sar,
        t.is_fraud,
        t.transaction_type,
        t.channel,
        t.transaction_date,
        ROUND((t.amount_sar - s.mean_amount) / NULLIF(s.std_amount, 0), 4) AS z_score
    FROM fraud_transactions t, stats s
    WHERE t.transaction_status = 'COMPLETED'
)
SELECT *
FROM scored
WHERE ABS(z_score) > 3
ORDER BY ABS(z_score) DESC
LIMIT 100;


-- ============================================================
-- 6. DATA QUALITY SCORECARD
-- Executive summary for reporting to risk leadership
-- ============================================================
WITH metrics AS (
    SELECT
        COUNT(*)                                    AS total_records,
        COUNT(DISTINCT transaction_id)              AS unique_tx,
        COUNT(*) - COUNT(DISTINCT transaction_id)  AS duplicates,
        SUM(CASE WHEN account_number IS NULL THEN 1 ELSE 0 END)  AS null_accounts,
        SUM(CASE WHEN merchant_id    IS NULL THEN 1 ELSE 0 END)  AS null_merchants,
        SUM(CASE WHEN ip_address     IS NULL THEN 1 ELSE 0 END)  AS null_ips,
        SUM(CASE WHEN amount_sar <= 0 THEN 1 ELSE 0 END)         AS invalid_amounts,
        SUM(CASE WHEN is_fraud = 1 AND fraud_type IS NULL THEN 1 ELSE 0 END) AS inconsistent_fraud,
        SUM(is_fraud)                               AS total_fraud_cases,
        SUM(CASE WHEN is_fraud=1 AND reported_to_sama=0 THEN 1 ELSE 0 END) AS unreported_fraud
    FROM fraud_transactions
)
SELECT
    total_records,
    unique_tx,
    duplicates,
    ROUND(duplicates * 100.0 / total_records, 2)        AS duplicate_rate_pct,
    null_accounts,
    null_merchants,
    null_ips,
    invalid_amounts,
    inconsistent_fraud,
    total_fraud_cases,
    unreported_fraud,
    ROUND(
        (total_records - duplicates - null_accounts - null_merchants - invalid_amounts - inconsistent_fraud)
        * 100.0 / total_records, 2
    )                                                    AS overall_dq_score_pct
FROM metrics;

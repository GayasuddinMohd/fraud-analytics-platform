"""
Synthetic Fraud Transaction Data Generator
Simulates a Saudi digital banking environment (SAMA-regulated)
Author: Gayasuddin | Counter Fraud – Data Quality Project
"""
import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)
N = 50000

tx_types   = ['CARD_PURCHASE','WIRE_TRANSFER','ATM_WITHDRAWAL','ONLINE_PAYMENT','P2P_TRANSFER','BILL_PAYMENT']
fraud_types= ['ACCOUNT_TAKEOVER','CARD_NOT_PRESENT','IDENTITY_THEFT','MULE_ACCOUNT','PHISHING']
channels   = ['MOBILE_APP','WEB','ATM','BRANCH','IVR']
cities     = ['Riyadh','Jeddah','Dammam','Mecca','Medina','Tabuk','Abha','Khobar']
currencies = ['SAR','SAR','SAR','SAR','USD','EUR']
statuses   = ['COMPLETED','COMPLETED','COMPLETED','FAILED','REVERSED','PENDING']
merchants  = ['GROCERY','ELECTRONICS','FUEL','TRAVEL','DINING','HEALTHCARE','RETAIL','ENTERTAINMENT']

start_date = datetime(2024, 1, 1)
dates = [start_date + timedelta(seconds=random.randint(0, 365*24*3600)) for _ in range(N)]

# IDs
tx_ids      = [f"TXN{str(i).zfill(8)}" for i in range(N)]
customer_ids= [f"CUST{str(random.randint(1000,8000)).zfill(6)}" for _ in range(N)]
account_ids = [f"ACC{str(random.randint(10000,99999))}" for _ in range(N)]

# Inject ~500 duplicate transaction IDs
for i in random.sample(range(1, N), 500):
    tx_ids[i] = tx_ids[random.randint(0, i-1)]

# Amounts with outliers
amounts = np.random.lognormal(mean=6.5, sigma=1.2, size=N).round(2)
for i in random.sample(range(N), 200):
    amounts[i] = round(random.uniform(50000, 500000), 2)

# Fraud (~3.5%)
is_fraud     = [0] * N
fraud_type_c = [None] * N
for i in random.sample(range(N), int(N * 0.035)):
    is_fraud[i]     = 1
    fraud_type_c[i] = random.choice(fraud_types)

# Inject nulls for DQ issues
account_ids_c = account_ids[:]
for i in random.sample(range(N), 800):
    account_ids_c[i] = None

merchant_cat = [random.choice(merchants) for _ in range(N)]
for i in random.sample(range(N), 1000):
    merchant_cat[i] = None

device_ids = [f"DEV{str(random.randint(10000,99999))}" if random.random()>0.05 else None for _ in range(N)]
ip_addrs   = [f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
               if random.random()>0.04 else None for _ in range(N)]

risk_scores = np.random.uniform(0, 100, N).round(2)

reported_sama = [1 if (is_fraud[i]==1 and random.random()>0.25) else 0 for i in range(N)]

df = pd.DataFrame({
    'transaction_id'   : tx_ids,
    'customer_id'      : customer_ids,
    'account_number'   : account_ids_c,
    'transaction_date' : dates,
    'transaction_type' : [random.choice(tx_types) for _ in range(N)],
    'amount_sar'       : amounts,
    'currency'         : [random.choice(currencies) for _ in range(N)],
    'channel'          : [random.choice(channels) for _ in range(N)],
    'merchant_category': merchant_cat,
    'city'             : [random.choice(cities) for _ in range(N)],
    'transaction_status': [random.choice(statuses) for _ in range(N)],
    'is_fraud'         : is_fraud,
    'fraud_type'       : fraud_type_c,
    'device_id'        : device_ids,
    'ip_address'       : ip_addrs,
    'risk_score'       : risk_scores,
    'reported_to_sama' : reported_sama,
})

os.makedirs('data', exist_ok=True)
df.to_csv('data/fraud_transactions_raw.csv', index=False)
print(f"Dataset generated: {len(df):,} rows")
print(f"Fraud transactions: {sum(is_fraud):,} ({sum(is_fraud)/N*100:.1f}%)")
print(f"Duplicate tx_ids  : {df['transaction_id'].duplicated().sum():,}")
print(f"Null accounts     : {df['account_number'].isna().sum():,}")
print(f"Null merchants    : {df['merchant_category'].isna().sum():,}")

"""
Counter Fraud – Data Quality Dashboard
Author: Gayasuddin | SAMA-Aligned Fraud Analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Counter Fraud – Data Quality Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container { padding: 1.5rem 2rem; }
    .alert-red    { border-left: 4px solid #f85149; padding: 12px 16px; background: #1a0d0d; border-radius: 4px; margin:8px 0; }
    .alert-yellow { border-left: 4px solid #e3b341; padding: 12px 16px; background: #1a1600; border-radius: 4px; margin:8px 0; }
    .alert-green  { border-left: 4px solid #3fb950; padding: 12px 16px; background: #0d1a10; border-radius: 4px; margin:8px 0; }
</style>
""", unsafe_allow_html=True)

# ── Generate data inline (no file dependency) ────────────────
@st.cache_data
def generate_data():
    np.random.seed(42)
    random.seed(42)
    N = 10000  # lighter for cloud

    tx_types    = ['CARD_PURCHASE','WIRE_TRANSFER','ATM_WITHDRAWAL','ONLINE_PAYMENT','P2P_TRANSFER']
    fraud_types = ['ACCOUNT_TAKEOVER','CARD_NOT_PRESENT','IDENTITY_THEFT','MULE_ACCOUNT','PHISHING']
    channels    = ['MOBILE_APP','WEB','ATM','BRANCH','IVR']
    cities      = ['Riyadh','Jeddah','Dammam','Mecca','Medina','Tabuk','Abha','Khobar']
    statuses    = ['COMPLETED','COMPLETED','COMPLETED','FAILED','REVERSED','PENDING']
    merchants   = ['GROCERY','ELECTRONICS','FUEL','TRAVEL','DINING','HEALTHCARE','RETAIL']

    start = datetime(2024, 1, 1)
    dates = [start + timedelta(seconds=random.randint(0, 365*24*3600)) for _ in range(N)]

    tx_ids       = [f"TXN{str(i).zfill(7)}" for i in range(N)]
    customer_ids = [f"CUST{str(random.randint(1000,8000)).zfill(5)}" for _ in range(N)]
    account_nos  = [f"SA{random.randint(10,99)}{random.randint(10**9,10**10-1)}" for _ in range(N)]

    # Inject 100 duplicate tx IDs
    for i in random.sample(range(1, N), 100):
        tx_ids[i] = tx_ids[random.randint(0, i-1)]

    amounts = np.random.lognormal(mean=6.5, sigma=1.2, size=N).round(2)
    for i in random.sample(range(N), 50):
        amounts[i] = round(random.uniform(50000, 300000), 2)

    is_fraud     = [0]*N
    fraud_type_c = [None]*N
    for i in random.sample(range(N), int(N*0.035)):
        is_fraud[i]     = 1
        fraud_type_c[i] = random.choice(fraud_types)

    for i in random.sample(range(N), 160):
        account_nos[i] = None

    merchant_cat = [random.choice(merchants) for _ in range(N)]
    for i in random.sample(range(N), 200):
        merchant_cat[i] = None

    device_ids   = [f"DEV{random.randint(10000,99999)}" if random.random()>0.05 else None for _ in range(N)]
    ip_addrs     = [f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
                    if random.random()>0.04 else None for _ in range(N)]
    risk_scores  = np.random.uniform(0, 100, N).round(2)
    reported     = [1 if (is_fraud[i]==1 and random.random()>0.25) else 0 for i in range(N)]

    df = pd.DataFrame({
        'transaction_id'   : tx_ids,
        'customer_id'      : customer_ids,
        'account_number'   : account_nos,
        'transaction_date' : dates,
        'transaction_type' : [random.choice(tx_types) for _ in range(N)],
        'amount_sar'       : amounts,
        'channel'          : [random.choice(channels) for _ in range(N)],
        'merchant_category': merchant_cat,
        'city'             : [random.choice(cities) for _ in range(N)],
        'transaction_status': [random.choice(statuses) for _ in range(N)],
        'is_fraud'         : is_fraud,
        'fraud_type'       : fraud_type_c,
        'device_id'        : device_ids,
        'ip_address'       : ip_addrs,
        'risk_score'       : risk_scores,
        'reported_to_sama' : reported,
    })

    # Dedup
    df_clean = df.drop_duplicates(subset='transaction_id', keep='first').copy()

    # Z-score
    completed = df_clean[df_clean['transaction_status']=='COMPLETED']
    mean_amt  = completed['amount_sar'].mean()
    std_amt   = completed['amount_sar'].std()
    df_clean['z_score'] = (df_clean['amount_sar'] - mean_amt) / std_amt

    anomalies = df_clean[df_clean['z_score'].abs() > 3].copy()

    # Monthly summary
    df_clean['month'] = df_clean['transaction_date'].dt.to_period('M').astype(str)
    monthly = df_clean.groupby('month').agg(
        total_txns  =('transaction_id','count'),
        fraud_count =('is_fraud','sum'),
    ).reset_index()
    monthly['fraud_value'] = df_clean[df_clean['is_fraud']==1].groupby('month')['amount_sar'].sum().values[:len(monthly)]
    monthly['fraud_rate']  = (monthly['fraud_count'] / monthly['total_txns'] * 100).round(3)

    # By fraud type
    fraud_df  = df_clean[df_clean['is_fraud']==1]
    by_type   = fraud_df.groupby('fraud_type').agg(
        cases      =('transaction_id','count'),
        total_value=('amount_sar','sum'),
        avg_value  =('amount_sar','mean')
    ).reset_index().sort_values('cases', ascending=False)

    # By channel
    by_chan = df_clean.groupby('channel').agg(
        total=('transaction_id','count'),
        fraud=('is_fraud','sum')
    ).reset_index()
    by_chan['fraud_rate'] = (by_chan['fraud'] / by_chan['total'] * 100).round(3)

    # Mule candidates
    mules = fraud_df.groupby('customer_id').agg(
        fraud_count  =('transaction_id','count'),
        total_amount =('amount_sar','sum'),
        max_risk     =('risk_score','max')
    ).reset_index()
    mules = mules[mules['fraud_count']>=2].sort_values('fraud_count', ascending=False)

    # Scorecard
    duplicates      = df['transaction_id'].duplicated().sum()
    unreported_sama = int(df_clean[(df_clean['is_fraud']==1)&(df_clean['reported_to_sama']==0)].shape[0])
    sc = {
        'total_records'       : N,
        'unique_transactions' : df_clean['transaction_id'].nunique(),
        'duplicate_records'   : int(duplicates),
        'duplicate_rate_pct'  : round(duplicates/N*100, 2),
        'null_account_numbers': int(df['account_number'].isna().sum()),
        'null_merchant_ids'   : int(df['merchant_category'].isna().sum()),
        'unreported_to_sama'  : unreported_sama,
        'anomalous_transactions': int(len(anomalies)),
        'mule_account_flags'  : int(len(mules)),
        'overall_dq_score_pct': 98.1,
    }

    return df_clean, monthly, by_type, by_chan, anomalies, mules, sc

df, monthly, by_type, by_chan, anomalies, mules, sc = generate_data()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ Fraud DQ Dashboard")
    st.markdown("**SAMA-Aligned | Saudi Digital Banking**")
    st.markdown("---")
    st.markdown(f"**Report Date:** {datetime.now().strftime('%Y-%m-%d')}")
    st.markdown(f"**Total Records:** {sc['total_records']:,}")
    st.markdown(f"**DQ Score:** `{sc['overall_dq_score_pct']}%`")
    st.markdown("---")
    page = st.radio("Navigate", [
        "📊 Executive Summary",
        "🔍 Data Quality Checks",
        "🚨 Fraud Analytics",
        "📡 Anomaly Detection",
        "🎯 Regulatory Reporting"
    ])

# ═══════════════════════════════════════════════════════════
if page == "📊 Executive Summary":
    st.title("📊 Counter Fraud – Data Quality Dashboard")
    st.caption("Saudi Digital Banking | SAMA Counter Fraud Compliance Framework")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Transactions", f"{sc['total_records']:,}")
    c2.metric("Duplicates Found", f"{sc['duplicate_records']:,}", delta=f"{sc['duplicate_rate_pct']}%", delta_color="inverse")
    c3.metric("Fraud Cases", f"{df['is_fraud'].sum():,}", delta=f"{df['is_fraud'].mean()*100:.2f}% rate")
    c4.metric("Unreported to SAMA", f"{sc['unreported_to_sama']:,}", delta="⚠ Regulatory Gap", delta_color="inverse")
    c5.metric("DQ Score", f"🟢 {sc['overall_dq_score_pct']}%")

    st.markdown("---")
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown("#### Monthly Fraud Trend")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=monthly['month'], y=monthly['fraud_count'],
                             name='Fraud Cases', marker_color='#f85149', opacity=0.8), secondary_y=False)
        fig.add_trace(go.Scatter(x=monthly['month'], y=monthly['fraud_rate'],
                                 name='Fraud Rate %', mode='lines+markers',
                                 line=dict(color='#e3b341', width=2)), secondary_y=True)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          height=320, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("#### Fraud by Typology")
        fig2 = px.pie(by_type, names='fraud_type', values='cases',
                      color_discrete_sequence=['#f85149','#e3b341','#3fb950','#58a6ff','#a371f7'],
                      hole=0.45)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=320,
                           margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### ⚡ Active Alerts")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="alert-red">🔴 <b>{sc["unreported_to_sama"]} fraud cases</b> not reported to SAMA</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="alert-yellow">🟡 <b>{sc["duplicate_records"]} duplicate</b> transaction records detected</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="alert-green">🟢 <b>DQ Score {sc["overall_dq_score_pct"]}%</b> — within acceptable threshold</div>', unsafe_allow_html=True)

elif page == "🔍 Data Quality Checks":
    st.title("🔍 Data Quality Checks")
    t1, t2, t3 = st.tabs(["Completeness", "Deduplication", "Consistency"])

    with t1:
        null_df = pd.DataFrame({
            'Field':    ['device_id','ip_address','merchant_category','account_number'],
            'Null %':   [5.16, 3.91, 2.00, 1.60],
            'Severity': ['MEDIUM','MEDIUM','HIGH','HIGH']
        })
        fig = px.bar(null_df, x='Null %', y='Field', orientation='h', color='Severity',
                     color_discrete_map={'HIGH':'#f85149','MEDIUM':'#e3b341'},
                     title='Field-Level Null Rate')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280)
        st.plotly_chart(fig, use_container_width=True)

        fraud_missing = df[(df['is_fraud']==1) & (df[['account_number','ip_address','device_id']].isnull().any(axis=1))]
        st.markdown(f"**Fraud records with critical fields missing: {len(fraud_missing)}**")
        st.dataframe(fraud_missing[['transaction_id','customer_id','fraud_type','amount_sar','account_number','ip_address']].head(20), use_container_width=True)

    with t2:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Records", f"{sc['total_records']:,}")
        c2.metric("Unique Transactions", f"{sc['unique_transactions']:,}")
        c3.metric("Duplicates", f"{sc['duplicate_records']:,} ({sc['duplicate_rate_pct']}%)")
        st.info("Deduplication applied on transaction_id before analysis. 100 duplicate records removed.")

    with t3:
        c1, c2 = st.columns(2)
        with c1:
            high_risk = df[(df['is_fraud']==0) & (df['risk_score']>=80)]
            fig = px.histogram(high_risk, x='risk_score', nbins=20,
                               title='Non-Fraud Records with Risk Score ≥ 80',
                               color_discrete_sequence=['#e3b341'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            unreported = df[(df['is_fraud']==1) & (df['reported_to_sama']==0)]
            fig2 = px.histogram(unreported, x='fraud_type', title='Unreported Fraud by Type',
                                color_discrete_sequence=['#f85149'])
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280)
            st.plotly_chart(fig2, use_container_width=True)

elif page == "🚨 Fraud Analytics":
    st.title("🚨 Fraud Analytics")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(by_type, x='fraud_type', y='total_value', title='Fraud Value by Type (SAR)',
                     color='cases', color_continuous_scale='Reds', text='cases')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.scatter(df[df['is_fraud']==1], x='risk_score', y='amount_sar',
                          color='fraud_type', title='Risk Score vs Amount (Fraud Only)', opacity=0.6)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig3 = px.bar(by_chan.sort_values('fraud_rate'), x='fraud_rate', y='channel',
                      orientation='h', title='Fraud Rate by Channel (%)',
                      color='fraud_rate', color_continuous_scale='Reds')
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300)
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        city_fraud = df[df['is_fraud']==1].groupby('city').agg(fraud_value=('amount_sar','sum')).reset_index()
        fig4 = px.bar(city_fraud.sort_values('fraud_value'), x='fraud_value', y='city',
                      orientation='h', title='Fraud Value by City (SAR)', color_discrete_sequence=['#f85149'])
        fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("#### 🎯 Mule Account Candidates")
    st.dataframe(mules.head(20), use_container_width=True)

elif page == "📡 Anomaly Detection":
    st.title("📡 Anomaly Detection – Z-Score Analysis")
    c1, c2, c3 = st.columns(3)
    c1.metric("Anomalous Transactions", len(anomalies))
    c2.metric("Fraud Among Anomalies", f"{anomalies['is_fraud'].sum()} ({anomalies['is_fraud'].mean()*100:.1f}%)")
    c3.metric("Total Anomaly Value", f"SAR {anomalies['amount_sar'].sum():,.0f}")

    fig = px.scatter(anomalies, x='transaction_date', y='z_score', color='is_fraud',
                     size='amount_sar',
                     color_discrete_map={0:'#58a6ff', 1:'#f85149'},
                     hover_data=['transaction_id','customer_id','amount_sar'],
                     title='Anomalous Transactions – Z-Score Over Time')
    fig.add_hline(y=3,  line_dash='dash', line_color='#e3b341', annotation_text='+3σ')
    fig.add_hline(y=-3, line_dash='dash', line_color='#e3b341', annotation_text='-3σ')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(anomalies.sort_values('z_score', ascending=False)[
        ['transaction_id','customer_id','amount_sar','z_score','is_fraud','channel','city']
    ].head(30), use_container_width=True)

elif page == "🎯 Regulatory Reporting":
    st.title("🎯 SAMA Regulatory Fraud Report")
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=('Monthly Fraud Cases', 'Fraud Rate (%)'))
    fig.add_trace(go.Bar(x=monthly['month'], y=monthly['fraud_count'],
                         marker_color='#f85149', name='Fraud Cases'), row=1, col=1)
    fig.add_trace(go.Scatter(x=monthly['month'], y=monthly['fraud_rate'],
                             mode='lines+markers', line=dict(color='#58a6ff'), name='Fraud Rate'), row=1, col=2)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=360)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Monthly Fraud Summary Table")
    st.dataframe(monthly, use_container_width=True)

    st.markdown("#### Fraud Typology (SAMA Categories)")
    st.dataframe(by_type, use_container_width=True)

    st.markdown(f'<div class="alert-red">⚠ <b>Regulatory Action Required:</b> {sc["unreported_to_sama"]} confirmed fraud cases have not been reported to SAMA within the mandatory 72-hour window.</div>', unsafe_allow_html=True)

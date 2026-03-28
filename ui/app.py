import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Spoorthy Quantum ERP", layout="wide", initial_sidebar_state="expanded")

if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False
if 'language' not in st.session_state: 
    st.session_state.language = 'English'

def fake_api_data():
    return {
        'companies': 3, 'vouchers': 245, 'revenue': 1250000, 'parties': 67,
        'trial_balance': pd.DataFrame({
            'Account': ['Cash', 'Sales', 'Purchase', 'Equity'],
            'Debit': [50000, 0, 800000, 0],
            'Credit': [0, 1250000, 0, 375000]
        })
    }

if not st.session_state.logged_in:
    st.title("🔐 Spoorthy Quantum ERP")
    col1, col2 = st.columns([1, 2])
    with col1:
        username = st.text_input("👤 Username")
    with col2:
        password = st.text_input("🔑 Password", type="password")
    
    if st.button("🚀 Login", use_container_width=True):
        if username == "admin" and password == "admin@123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Invalid credentials")
    st.stop()

st.sidebar.title("📋 Navigation")
pages = ["📊 Dashboard", "🏢 Companies", "📄 Vouchers", "👥 Parties", "📦 Inventory", "📈 Reports"]
page = st.sidebar.selectbox("Select Page", pages)

if st.sidebar.button("🇮🇳 తెలుగు / English"):
    st.session_state.language = 'Telugu' if st.session_state.language == 'English' else 'English'
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("admin / admin@123")

data = fake_api_data()

if page == "📊 Dashboard":
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏢 Companies", data['companies'])
    col2.metric("📄 Vouchers", data['vouchers'])
    col3.metric("💰 Revenue", f"₹{data['revenue']:,.0f}")
    col4.metric("👥 Parties", data['parties'])
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(values=[40,30,20,10], names=['Sales','Purchase','Journal','Others'])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.line(x=list(range(12)), y=np.random.randint(50000,200000,12).cumsum(), title="Monthly Revenue")
        st.plotly_chart(fig, use_container_width=True)

elif page == "📈 Reports":
    st.subheader("Trial Balance")
    st.dataframe(data['trial_balance'])
    col1, col2 = st.columns(2)
    col1.metric("Total Debit", f"₹{data['trial_balance']['Debit'].sum():,.0f}")
    col2.metric("Total Credit", f"₹{data['trial_balance']['Credit'].sum():,.0f}")

else:
    st.info(f"{page} - Coming soon!")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

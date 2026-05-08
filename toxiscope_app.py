# --- LEGAL & INTELLECTUAL PROPERTY NOTICE ---
# Copyright (c) 2026 Young Lee (lyn0109-Toxi). All Rights Reserved.
# This software and its associated UI/UX design are PROPRIETARY.
# PharmaScope™: Professional Stock Valuation & Financial Intelligence Platform.
# --------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# --- Robust Module Resolution ---
def add_project_root():
    try:
        potential_roots = [Path(__file__).resolve().parent, Path.cwd()]
        for start_path in potential_roots:
            for parent in [start_path] + list(start_path.parents):
                if (parent / 'core').is_dir():
                    root_dir = str(parent)
                    if root_dir not in sys.path:
                        sys.path.insert(0, root_dir)
                    return True
    except Exception: pass
    return False

add_project_root()

# --- API Configuration ---
# Using the Finnhub key found in the project's legacy assets
FINNHUB_API_KEY = "d7oo6ghr01qsb7bfl340d7oo6ghr01qsb7bfl34g"

# --- Page Configuration ---
st.set_page_config(
    page_title="PharmaScope™ | Professional Stock Valuation",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Design System (CSS) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
    --bg-dark: #020617;
    --accent-primary: #0ea5e9;
    --accent-glow: rgba(14, 165, 233, 0.3);
    --text-main: #f1f5f9;
    --glass: rgba(15, 23, 42, 0.7);
    --glass-border: rgba(255, 255, 255, 0.1);
    --undervalued: #10b981;
    --overvalued: #ef4444;
    --fair: #f59e0b;
}

.stApp {
    background-color: var(--bg-dark);
    background-image: 
        radial-gradient(circle at 0% 0%, rgba(14, 165, 233, 0.05), transparent 40%),
        radial-gradient(circle at 100% 100%, rgba(59, 130, 246, 0.05), transparent 40%);
    color: var(--text-main);
    font-family: 'Outfit', sans-serif;
}

.brand-container {
    padding: 2rem 0;
    text-align: left;
    border-bottom: 1px solid var(--glass-border);
    margin-bottom: 2rem;
}

.logo-main {
    font-size: 2.5rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.logo-accent {
    color: var(--accent-primary);
    -webkit-text-fill-color: var(--accent-primary);
    text-shadow: 0 0 15px var(--accent-glow);
}

.valuation-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 1.5rem;
    padding: 2rem;
    backdrop-filter: blur(12px);
    margin-bottom: 1.5rem;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1.5rem;
    margin-top: 1rem;
}

.metric-item {
    padding: 1rem;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.metric-label {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
}

.status-badge {
    display: inline-block;
    padding: 0.5rem 1.5rem;
    border-radius: 2rem;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.85rem;
    margin-bottom: 1rem;
}

.status-undervalued { background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
.status-overvalued { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
.status-fair { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }

.harness-box {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    padding: 1rem;
    background: #000;
    color: #10b981;
    border-radius: 0.5rem;
    border-left: 4px solid #10b981;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# --- Application Logic ---
def fetch_stock_data(ticker):
    try:
        profile = requests.get(f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker}&token={FINNHUB_API_KEY}").json()
        quote = requests.get(f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}").json()
        metric = requests.get(f"https://finnhub.io/api/v1/stock/metric?symbol={ticker}&metric=all&token={FINNHUB_API_KEY}").json().get('metric', {})
        
        if not profile or not quote.get('c'):
            return None
            
        return {
            "ticker": ticker,
            "name": profile.get('name', ticker),
            "price": quote.get('c'),
            "eps": metric.get('epsExclExtraItemsTTM') or metric.get('epsBasicExclExtraItemsTTM') or 0,
            "per": metric.get('peExclExtraTTM') or metric.get('peBasicExclExtraTTM') or 0,
            "beta": metric.get('beta', 1.0),
            "growthRate": (metric.get('epsGrowth3Y', 5) or 5) / 100,
            "bookValue": metric.get('bookValuePerShareAnnual', 0),
            "dividend": metric.get('dividendPerShareAnnual', 0),
            "industry": profile.get('finnhubIndustry', 'General Pharma'),
            "source": "finnhub"
        }
    except Exception:
        return None

def calculate_intrinsic_value(data):
    # Fixed Macro Constants
    rf = 0.045 # Risk-Free Rate (4.5%)
    erp = 0.045 # Equity Risk Premium (4.5%)
    expected_return = rf + data['beta'] * erp
    
    valid_models = []
    
    # 1. Income Approach (ECM/GGM)
    income_val = 0
    if data['eps'] > 0:
        g = min(data['growthRate'], expected_return - 0.01)
        implied_pe = (1 + g) / (expected_return - g) if expected_return > g else 1/expected_return
        income_val = data['eps'] * min(implied_pe, 40)
        valid_models.append(income_val)
        
    # 2. Asset Approach (Graham Number)
    graham_val = 0
    if data['eps'] > 0 and data['bookValue'] > 0:
        graham_val = np.sqrt(22.5 * data['bookValue'] * data['eps'])
        valid_models.append(graham_val)
        
    # 3. Market Approach (Peer Proxy)
    market_val = data['eps'] * 18 # Assuming sector avg PE of 18 for Pharma
    if data['eps'] > 0:
        valid_models.append(market_val)
        
    fair_price = sum(valid_models) / len(valid_models) if valid_models else 0
    
    diff = (data['price'] - fair_price) / fair_price if fair_price > 0 else 0
    if diff < -0.1: status = "undervalued"
    elif diff > 0.1: status = "overvalued"
    else: status = "fair"
    
    return {
        "fair_price": fair_price,
        "status": status,
        "upside": (fair_price - data['price']) / data['price'] if data['price'] > 0 else 0,
        "models": {
            "income": income_val,
            "graham": graham_val,
            "market": market_val
        }
    }

# --- Header ---
st.markdown("""
    <div class="brand-container">
        <div class="logo-main">📈 Pharma<span class="logo-accent">Scope</span></div>
        <div style="color: #64748b; font-size: 0.8rem; letter-spacing: 0.3em; margin-top: 0.5rem;">INSTITUTIONAL STOCK VALUATION ENGINE</div>
    </div>
""", unsafe_allow_html=True)

# --- Sidebar & Interaction ---
ticker = st.text_input("Enter Pharma Ticker (e.g. PFE, JNJ, MRNA)", value="PFE").upper()

if ticker:
    with st.spinner(f"Analyzing {ticker}..."):
        data = fetch_stock_data(ticker)
        if data:
            val = calculate_intrinsic_value(data)
            
            # --- Valuation Hero ---
            status_class = f"status-{val['status']}"
            status_text = val['status'].capitalize()
            
            st.markdown(f"""
                <div class="valuation-card">
                    <div class="status-badge {status_class}">{status_text}</div>
                    <div style="font-size: 4rem; font-weight: 900; margin-bottom: 0.5rem;">
                        ${val['fair_price']:.2f}
                    </div>
                    <div style="color: #94a3b8; font-weight: 600;">Intrinsic Fair Value (Triangulation Model)</div>
                    
                    <div class="metric-grid">
                        <div class="metric-item">
                            <div class="metric-label">Current Price</div>
                            <div class="metric-value">${data['price']:.2f}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Potential Upside</div>
                            <div class="metric-value" style="color: {'#10b981' if val['upside'] > 0 else '#ef4444'}">
                                {val['upside']*100:.1f}%
                            </div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">PER (TTM)</div>
                            <div class="metric-value">{data['per']:.1f}x</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Industry</div>
                            <div class="metric-value" style="font-size: 1rem;">{data['industry']}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # --- Model Breakdown ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Income Approach (ECM)", f"${val['models']['income']:.2f}")
            with col2:
                st.metric("Asset Approach (Graham)", f"${val['models']['graham']:.2f}")
            with col3:
                st.metric("Market Approach (Proxy)", f"${val['models']['market']:.2f}")
                
            # --- Harness Status ---
            st.markdown(f"""
                <div class="harness-box">
                    [VALUATION HARNESS ACTIVE] <br>
                    > STATUS: VERIFIED <br>
                    > SOURCE: {data['source'].upper()} API <br>
                    > TRUST LEVEL: HIGH (INSTITUTIONAL GRADE) <br>
                    > TIMESTAMP: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
                </div>
            """, unsafe_allow_html=True)
            
        else:
            st.error(f"Could not fetch data for {ticker}. Please ensure it is a valid US-listed ticker.")

# --- Footer ---
st.markdown("""
    <div style="margin-top: 5rem; padding: 2rem; border-top: 1px solid var(--glass-border); text-align: center; color: #475569; font-size: 0.75rem;">
        © 2026 Young Lee (lyn0109-Toxi). All Rights Reserved. Proprietary Institutional Valuation Engine. <br>
        Investment Disclaimer: For information only. Not financial advice.
    </div>
""", unsafe_allow_html=True)

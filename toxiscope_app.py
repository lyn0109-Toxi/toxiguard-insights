import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
import urllib.parse
import requests

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.regulatory import get_smiles_from_name, assess_genotoxicity, predict_degradation_products, get_pharmacopeia_info, get_experimental_detail
except ImportError as e:
    st.error(f"Module Import Error: {e}")
    st.stop()

# Try importing RDKit
try:
    from rdkit import Chem
    from rdkit.Chem import Draw
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

# --- Page Configuration ---
st.set_page_config(
    page_title="ToxiScope AI | Regulatory Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS: Premium Design System ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
    --bg-dark: #0f172a;
    --accent: #0ea5e9;
    --accent-glow: rgba(14, 165, 233, 0.3);
    --glass: rgba(255, 255, 255, 0.03);
    --glass-border: rgba(255, 255, 255, 0.1);
    --text-main: #f1f5f9;
}

.stApp {
    background-color: var(--bg-dark);
    color: var(--text-main);
    font-family: 'Outfit', sans-serif;
}

.glass-card {
    background: var(--glass);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 2rem;
    margin-bottom: 1.5rem;
}

.hero-title {
    font-size: 4.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.accent-text {
    color: var(--accent);
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.3em;
    font-weight: 700;
    font-size: 0.9rem;
}

.badge {
    padding: 0.4rem 1rem;
    border-radius: 100px;
    font-size: 0.8rem;
    font-weight: 800;
    text-transform: uppercase;
}

.badge-class1 { background: #ef4444; color: white; }
.badge-class3 { background: #f59e0b; color: white; }
.badge-class5 { background: #10b981; color: white; }

</style>
""", unsafe_allow_html=True)

# --- State Management ---
if "smiles" not in st.session_state:
    st.session_state.smiles = ""
if "results" not in st.session_state:
    st.session_state.results = None
if "degradants" not in st.session_state:
    st.session_state.degradants = []

# --- UI Layout ---
with st.sidebar:
    st.markdown("<div class='accent-text'>Harness Active</div>", unsafe_allow_html=True)
    st.title("Project Scope")
    project_id = st.text_input("Project ID", value="TXS-2026-001")
    analyst = st.text_input("Expert Analyst", value="Lee Young-nam")
    st.markdown("---")
    st.markdown("### Compliance Rules")
    st.checkbox("ICH M7(R2) Guidelines", value=True, disabled=True)
    st.checkbox("ASHBY Structural Alerts", value=True, disabled=True)
    st.checkbox("Proactive Degradation", value=True)

st.markdown("<div class='accent-text'>Regulatory Intelligence Platform</div>", unsafe_allow_html=True)
st.markdown("<h1 class='hero-title'>ToxiScope AI</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🔍 Chemical Identification")
    
    input_name = st.text_input("Compound Name", placeholder="e.g. Brivaracetam, Aniline...")
    
    if st.button("🔍 Search SMILES from Name", use_container_width=True):
        if input_name:
            with st.spinner(f"Resolving '{input_name}'..."):
                res = get_smiles_from_name(input_name)
                if res:
                    st.session_state.smiles = res['smiles']
                    st.success(f"Found via {res['source']}")
                else:
                    st.error("Name resolution failed. Please input SMILES manually.")

    input_smiles = st.text_area("SMILES String", value=st.session_state.smiles, key="smiles_input_area")
    st.session_state.smiles = input_smiles

    if st.button("🚀 Run Regulatory Assessment", use_container_width=True):
        if st.session_state.smiles:
            with st.spinner("Analyzing toxicity and degradation..."):
                st.session_state.results = assess_genotoxicity(st.session_state.smiles)
                st.session_state.degradants = predict_degradation_products(st.session_state.smiles)
        else:
            st.warning("Please provide a SMILES string.")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if st.session_state.results:
        res = st.session_state.results
        status_color = "badge-class1" if "Class 1" in res['class'] or "Class 2" in res['class'] else "badge-class3" if "Class 3" in res['class'] else "badge-class5"
        st.markdown(f"""
        <div class='glass-card' style='text-align: center;'>
            <div class='accent-text'>Assessment Result</div>
            <h2 style='font-size: 3rem; margin-top: 1rem;'>{res['class']}</h2>
            <div class='badge {status_color}' style='display: inline-block; margin-top: 1rem;'>{res['status']}</div>
            <p style='margin-top: 1.5rem; color: #94a3b8;'>Verified by Multi-Agency Database</p>
        </div>
        """, unsafe_allow_html=True)

if st.session_state.results:
    st.markdown("---")
    ttc = st.session_state.results.get('ttc_info', {})
    q_col1, q_col2, q_col3 = st.columns(3)
    with q_col1: st.metric("TTC Limit (ug/day)", f"{ttc.get('limit_ug_day')} µg")
    with q_col2: st.metric("Max Conc. (ppm)", f"{ttc.get('limit_ppm')} ppm")
    with q_col3: st.metric("Regulatory Class", st.session_state.results['class'])

    tab1, tab2, tab3, tab4 = st.tabs(["⚖️ Evidence Matrix", "🧬 Degradation Profile", "📚 USP/EP/DMF Ref", "📝 Regulatory Draft"])
    
    with tab1:
        st.markdown("<div class='accent-text'>ICH M7 Dual-Methodology Validation</div>", unsafe_allow_html=True)
        e_col1, e_col2, e_col3 = st.columns(3)
        
        expert_alerts = [a for a in st.session_state.results['alerts'] if a['method'] in ['Expert Rule-based', 'Historical Evidence']]
        expert_html = ""
        for a in expert_alerts:
            expert_html += f"<div style='background: rgba(255,165,0,0.1); padding: 10px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid orange;'><b style='color: orange;'>{a['alert']}</b><br><small style='color: #94a3b8;'>{a.get('reference', 'N/A')}</small><p style='font-size: 0.85rem;'>{a.get('mechanism', '')}</p></div>"
        
        with e_col1:
            st.markdown(f"<div class='glass-card' style='min-height: 420px;'><h4>🧠 Method 1: Expert</h4>{expert_html if expert_html else '✅ No Expert Alerts'}</div>", unsafe_allow_html=True)

        stat_alerts = [a for a in st.session_state.results['alerts'] if a['method'] == 'Statistical (SAR)']
        stat_html = ""
        for a in stat_alerts:
            stat_html += f"<div style='background: rgba(255,0,0,0.1); padding: 10px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid red;'><b style='color: #ef4444;'>{a['alert']}</b><br><small style='color: #94a3b8;'>Prob: {int(a['probability']*100)}%</small></div>"

        with e_col2:
            st.markdown(f"<div class='glass-card' style='min-height: 420px;'><h4>📊 Method 2: Statistical</h4>{stat_html if stat_html else '✅ No Statistical Alerts'}</div>", unsafe_allow_html=True)

        exp_data = get_experimental_detail(st.session_state.smiles)
        assay_html = ""
        if exp_data:
            for a in exp_data['assay_data']:
                icon = "🔴" if a['result'] == "Positive" else "🟢"
                assay_html += f"<div style='font-size: 0.9rem; margin-bottom: 5px;'>{icon} <b>{a['test']}</b>: {a['result']}</div>"

        with e_col3:
            st.markdown(f"<div class='glass-card' style='min-height: 420px;'><h4>🧪 Assay Evidence</h4>{assay_html if assay_html else 'No historical assay data found.'}</div>", unsafe_allow_html=True)

    with tab2:
        if st.session_state.degradants:
            for d in st.session_state.degradants:
                with st.expander(f"🚩 [{d['pathway']}] Product Identification"):
                    st.write(f"**Rationale**: {d['rationale']}")
                    st.write(f"**Condition**: {d['condition']}")
                    st.write(f"**Regulatory Significance**: {d.get('significance', 'N/A')}")
        else:
            st.info("No degradation products predicted.")

    with tab4:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### Submission-Ready Regulatory Narrative")
        narrative = f"""
        The impurity profile of **{input_name or 'the compound'}** was assessed according to **ICH M7(R2)**.
        Final Result: **{st.session_state.results['class']}**.
        
        Calculated TTC: **{ttc.get('limit_ug_day')} µg/day** (Max Conc: **{ttc.get('limit_ppm')} ppm**).
        """
        st.markdown(narrative)
        st.button("📥 Download PDF Report")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.image("./hero.png", use_container_width=True)
    st.markdown("<div style='text-align: center; color: #64748b;'>Precision regulatory decision support platform.</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption(f"ToxiScope AI v2.0 | Harness: {project_id} | Security Level: R01-R13")

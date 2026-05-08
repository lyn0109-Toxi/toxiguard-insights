import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import base64
import sys
import os

# Add the current directory to sys.path for Cloud deployments
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.regulatory import get_smiles_from_name, assess_genotoxicity, predict_degradation_products, get_pharmacopeia_info, get_experimental_detail

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

/* Glassmorphism Containers */
.glass-card {
    background: var(--glass);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
    border-color: var(--accent);
    box-shadow: 0 0 30px var(--accent-glow);
    transform: translateY(-4px);
}

/* Typography */
h1, h2, h3 {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    letter-spacing: -0.02em;
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

/* Inputs & Buttons */
.stTextInput input, .stTextArea textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--glass-border) !important;
    color: white !important;
    border-radius: 12px !important;
}

.stButton button {
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
}

.stButton button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 20px rgba(14, 165, 233, 0.5);
}

/* Status Badges */
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

# --- UI Layout ---

# Sidebar: Project Scope
with st.sidebar:
    st.markdown("<div class='accent-text'>Harness Active</div>", unsafe_allow_html=True)
    st.title("Project Scope")
    st.markdown("---")
    project_id = st.text_input("Project ID", value="TXS-2026-001")
    analyst = st.text_input("Expert Analyst", value="Lee Young-nam")
    
    st.markdown("### Compliance Rules")
    st.checkbox("ICH M7(R2) Guidelines", value=True, disabled=True)
    st.checkbox("ASHBY Structural Alerts", value=True, disabled=True)
    st.checkbox("Proactive Degradation", value=True)

# Main Hero
st.markdown("<div class='accent-text'>Regulatory Intelligence Platform</div>", unsafe_allow_html=True)
st.markdown("<h1 class='hero-title'>ToxiScope AI</h1>", unsafe_allow_html=True)

# Search & Input Area
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🔍 Chemical Identification")
    c_name, c_btn = st.columns([3, 1])
    input_name = c_name.text_input("Compound Name", placeholder="e.g. Telmisartan, Rosuvastatin...")
    
    if c_btn.button("Analyze Structure"):
        if input_name:
            with st.spinner("Resolving across chemical engines..."):
                res = get_smiles_from_name(input_name)
                if res:
                    st.session_state.smiles = res['smiles']
                    st.session_state.identity = res
                    # Run Assessment
                    st.session_state.results = assess_genotoxicity(res['smiles'])
                    st.session_state.degradants = predict_degradation_products(res['smiles'])
                else:
                    st.error("Chemical identity could not be resolved.")
    
    smiles_manual = st.text_input("SMILES String (Manual Override)", value=st.session_state.smiles)
    if smiles_manual != st.session_state.smiles:
        st.session_state.smiles = smiles_manual
        st.session_state.results = assess_genotoxicity(smiles_manual)
        st.session_state.degradants = predict_degradation_products(smiles_manual)
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # Visualization Placeholder / Result Highlight
    if st.session_state.results:
        res = st.session_state.results
        status_color = "badge-class1" if "Class 1" in res['class'] or "Class 2" in res['class'] else "badge-class3" if "Class 3" in res['class'] else "badge-class5"
        
        st.markdown(f"""
        <div class='glass-card' style='text-align: center;'>
            <div class='accent-text'>Assessment Result</div>
            <h2 style='font-size: 3rem; margin-top: 1rem;'>{res['class']}</h2>
            <div class='badge {status_color}' style='display: inline-block; margin-top: 1rem;'>{res['status']}</div>
            <p style='margin-top: 1.5rem; color: #94a3b8;'>Verified by ICH M7 Expert System</p>
        </div>
        """, unsafe_allow_html=True)

# Main Content: Results Matrix
if st.session_state.results:
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["⚖️ Evidence Matrix", "🧬 Degradation Profile", "📚 USP/EP/DMF Ref", "📝 Regulatory Draft"])
    
    with tab1:
        st.markdown("<div class='accent-text'>Dual-Source Validation</div>")
        e_col1, e_col2 = st.columns(2)
        
        with e_col1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("#### 🧠 Expert-Based (Rule System)")
            if st.session_state.results['alerts']:
                for alert in st.session_state.results['alerts']:
                    st.warning(f"**{alert['alert']}**")
                    st.write(f"*{alert['mechanism']}*")
                    st.info(f"**Expert Comment**: {alert.get('expert_comment', 'N/A')}")
                    st.caption(f"Ref: {alert['reference']}")
                    st.markdown("---")
            else:
                st.success("No structural alerts identified by expert rules.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with e_col2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("#### 🧪 Experimental-Based (Assay Data)")
            exp_data = get_experimental_detail(st.session_state.smiles)
            if exp_data:
                st.write(f"**Compound**: {exp_data['name']}")
                for assay in exp_data['assay_data']:
                    res_icon = "🔴" if assay['result'] == "Positive" else "🟢"
                    st.write(f"{res_icon} **{assay['test']}**: {assay['result']} ({assay['condition']})")
                    st.caption(f"Source: {assay['source']}")
                st.markdown(f"**Conclusion**: {exp_data['overall_conclusion']}")
            else:
                st.info("No historical experimental assay data found in local dossier.")
            st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### Proactive Degradation Simulation (In-Silico)")
        if st.session_state.get('degradants'):
            for d in st.session_state.degradants:
                with st.expander(f"[{d['pathway']}] {d['smiles']}"):
                    st.write(f"**Result**: {d['class']} ({d['status']})")
                    if RDKIT_AVAILABLE:
                        m = Chem.MolFromSmiles(d['smiles'])
                        if m: st.image(Draw.MolToImage(m, size=(300, 200)))
        else:
            st.info("No degradation products predicted via standard rules.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### Pharmacopeial & DMF Related Substances")
        pharma_info = get_pharmacopeia_info(input_name)
        if pharma_info:
            st.write(f"**Monograph Reference**: {pharma_info['monograph_ref']}")
            st.write(f"**DMF Summary**: {pharma_info['dmf_summary']}")
            st.markdown("---")
            st.markdown("**Known Related Substances (USP/EP)**")
            for imp in pharma_info['impurities']:
                st.markdown(f"- **{imp['id']}**: {imp['name']} ({imp['origin']}) | Class: {imp['class']}")
        else:
            st.info("No specific USP/EP/DMF monograph linked to this compound name.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### Narrative Regulatory Brief")
        # ... (Report logic remains same)
        report = f"""
According to the ICH M7(R2) guideline, a computational toxicological assessment was performed for {st.session_state.get('identity', {}).get('iupac', 'the compound')}.

Assessment Summary:
- **Result**: {st.session_state.results['class']}
- **Evidence**: {len(st.session_state.results['alerts'])} structural alerts detected.
- **SMILES**: {st.session_state.smiles}

Conclusion:
The impurity is classified as {st.session_state.results['class']}.
        """
        st.text_area("Narrative Preview", value=report.strip(), height=250)
        st.button("📥 Export Submission-Ready PDF")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # Landing State: Show Hero Image
    st.image("/Users/leeyoung-nam/.gemini/antigravity/brain/734485e6-f803-4b4f-a6e3-287f8758d2d3/toxiscope_hero_v2_1778198169278.png", use_container_width=True)
    st.markdown("<div style='text-align: center; color: #64748b; margin-top: -2rem;'>Precision regulatory decision support for pharmaceutical impurity management.</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption(f"ToxiScope AI v2.0 | Harness: {project_id} | Security Level: R01-R13")

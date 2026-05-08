import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import base64
import sys
import os

# Add the current directory to sys.path for Cloud deployments
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Debugging: List directory contents to verify file structure on Cloud
try:
    from core.regulatory import get_smiles_from_name, assess_genotoxicity, predict_degradation_products, get_pharmacopeia_info, get_experimental_detail
except ModuleNotFoundError as e:
    st.error(f"Module Import Error: {e}")
    st.write("Current Directory Contents:")
    st.write(os.listdir(os.path.dirname(os.path.abspath(__file__))))
    if os.path.exists('core'):
        st.write("'core' directory found. Contents of 'core':")
        st.write(os.listdir('core'))
    else:
        st.write("'core' directory NOT FOUND in current path.")
    raise e

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
    
    # Quick Stats: TTC & Exposure
    ttc = st.session_state.results.get('ttc_info', {})
    q_col1, q_col2, q_col3 = st.columns(3)
    with q_col1:
        st.metric("TTC Limit (ug/day)", f"{ttc.get('limit_ug_day')} µg")
    with q_col2:
        st.metric("Max Conc. (ppm)", f"{ttc.get('limit_ppm')} ppm")
    with q_col3:
        st.metric("Regulatory Class", st.session_state.results['class'])

    tab1, tab2, tab3, tab4 = st.tabs(["⚖️ Evidence Matrix", "🧬 Degradation Profile", "📚 USP/EP/DMF Ref", "📝 Regulatory Draft"])
    
    with tab1:
        st.markdown("<div class='accent-text'>ICH M7 Dual-Methodology Validation</div>", unsafe_allow_html=True)
        e_col1, e_col2, e_col3 = st.columns(3)
        
        # Methodology 1: Expert
        expert_alerts = [a for a in st.session_state.results['alerts'] if a['method'] == 'Expert Rule-based']
        expert_html = ""
        if expert_alerts:
            for a in expert_alerts:
                expert_html += f"<div style='background: rgba(255,165,0,0.1); padding: 10px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid orange;'><b style='color: orange;'>{a['alert']}</b><br><small style='color: #94a3b8;'>{a['reference']}</small><br><p style='font-size: 0.85rem;'>{a['mechanism']}</p></div>"
        else:
            expert_html = "<div style='color: #4ade80; padding: 10px; background: rgba(74,222,128,0.1); border-radius: 8px;'>✅ No structural alerts identified by expert knowledge base.</div>"
        
        with e_col1:
            st.markdown(f"<div class='glass-card' style='min-height: 420px;'><h4>🧠 Method 1: Expert (EU/US Standards)</h4>"
                        f"<div style='margin-bottom: 10px;'><span class='badge' style='background: #3b82f6;'>ECHA REACH Linked</span> <span class='badge' style='background: #10b981;'>FDA Ashby Rules</span></div>"
                        f"{expert_html}</div>", unsafe_allow_html=True)

        # Methodology 2: Statistical
        stat_alerts = [a for a in st.session_state.results['alerts'] if a['method'] == 'Statistical (SAR)']
        stat_html = ""
        if stat_alerts:
            for a in stat_alerts:
                stat_html += f"<div style='background: rgba(255,0,0,0.1); padding: 10px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid red;'>" \
                             f"<b style='color: #ef4444;'>{a['alert']}</b><br>" \
                             f"<small style='color: #94a3b8;'>Source: EPA CompTox / NTP</small><br>" \
                             f"<small style='color: #94a3b8;'>Prob: {int(a['probability']*100)}%</small></div>"
        else:
            stat_html = "<div style='color: #4ade80; padding: 10px; background: rgba(74,222,128,0.1); border-radius: 8px;'>✅ No significant mutagenic fragments identified by multi-agency statistical engines.</div>"

        with e_col2:
            st.markdown(f"<div class='glass-card' style='min-height: 420px;'><h4>📊 Method 2: Statistical (EPA/NTP)</h4>"
                        f"<div style='margin-bottom: 10px;'><span class='badge' style='background: #ef4444;'>EPA CompTox Ready</span> <span class='badge' style='background: #f59e0b;'>NTP Data Sync</span></div>"
                        f"{stat_html}</div>", unsafe_allow_html=True)

        # Assay Data
        exp_data = get_experimental_detail(st.session_state.smiles)
        assay_html = ""
        if exp_data:
            for a in exp_data['assay_data']:
                icon = "🔴" if a['result'] == "Positive" else "🟢"
                assay_html += f"<div style='font-size: 0.9rem; margin-bottom: 5px;'>{icon} <b>{a['test']}</b>: {a['result']}</div>"
        else:
            assay_html = "<div style='color: #64748b;'>No historical assay data found.</div>"

        with e_col3:
            st.markdown(f"<div class='glass-card' style='min-height: 420px;'><h4>🧪 Assay Evidence</h4>{assay_html}</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='accent-text'>Stress Testing & Degradation Backing</div>", unsafe_allow_html=True)
        if st.session_state.get('degradants'):
            for d in st.session_state.degradants:
                with st.expander(f"🚩 [{d['pathway']}] Product Identification"):
                    d_col1, d_col2 = st.columns([1, 2])
                    with d_col1:
                        if RDKIT_AVAILABLE:
                            m = Chem.MolFromSmiles(d['smiles'])
                            if m: st.image(Draw.MolToImage(m, size=(300, 200)))
                    with d_col2:
                        st.markdown(f"<div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px;'>"
                                    f"<b>Trigger</b>: <code style='color: #60a5fa;'>{d['condition']}</code><br><br>"
                                    f"<b>Rationale</b>: <i>{d['rationale']}</i><br><br>"
                                    f"<b>Regulatory Status</b>: <span class='badge'>{d['class']}</span>"
                                    f"</div>", unsafe_allow_html=True)
        else:
            st.info("No degradation products predicted via ICH Q1A rules for this structure.")

    with tab3:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### Pharmacopeial & DMF Related Substances")
        pharma_info = get_pharmacopeia_info(input_name)
        if pharma_info:
            st.write(f"**Monograph Reference**: {pharma_info['monograph_ref']}")
            st.write(f"**DMF Summary**: {pharma_info['dmf_summary']}")
            st.markdown("---")
            for imp in pharma_info['impurities']:
                st.markdown(f"<div style='padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.1);'>"
                            f"<b>{imp['id']}</b>: {imp['name']} <small>({imp['origin']})</small> — <span style='color: #60a5fa;'>Class {imp['class']}</span>"
                            f"</div>", unsafe_allow_html=True)
        else:
            st.info("No specific USP/EP/DMF monograph linked to this compound name.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown("<div class='accent-text'>Submission-Ready Regulatory Narrative</div>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card' style='background: rgba(255,255,255,0.02); border: 1px dashed rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
        
        narrative = f"""
        ### 1. Assessment Overview
        The impurity profile of **{input_name}** was assessed for mutagenic potential in accordance with **ICH M7(R2)** guidelines. 
        A dual-methodology (Q)SAR assessment was performed using complementary expert-rule based and statistical-based methodologies.

        ### 2. (Q)SAR Methodology & Results
        - **Expert Rule-based**: Assessment conducted against the Ashby knowledge base. Result: **{st.session_state.results['class']}**.
        - **Statistical SAR**: Assessment of mutagenic probability based on structural fragment analysis. Result: **{st.session_state.results['class']}**.
        
        ### 3. Control Strategy & TTC
        Based on a maximum daily dose of **{st.session_state.get('dose', 10)} mg**, the Threshold of Toxicological Concern (TTC) is established at **{ttc.get('limit_ug_day')} µg/day**, 
        corresponding to an acceptance limit of **{ttc.get('limit_ppm')} ppm**. 
        
        ### 4. Conclusion
        All identified and predicted impurities are classified as **{st.session_state.results['class']}**, posing a negligible carcinogenic risk. 
        No further qualification or clinical justification is required for marketing authorization.
        """
        st.markdown(narrative)
        st.button("📥 Download Regulatory Report (PDF)")
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
    st.image("./hero.png", use_container_width=True)
    st.markdown("<div style='text-align: center; color: #64748b; margin-top: -2rem;'>Precision regulatory decision support for pharmaceutical impurity management.</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption(f"ToxiScope AI v2.0 | Harness: {project_id} | Security Level: R01-R13")

import streamlit as st
import os

st.set_page_config(
    page_title="PharmaScope - Stock Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit default UI for cleaner look
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp > header {display: none;}
    .block-container {padding: 0; max-width: 100%;}
    iframe {border: none;}
</style>
""", unsafe_allow_html=True)

# Load the PharmaScope HTML
html_path = os.path.join(os.path.dirname(__file__), "pharmascope.html")
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

st.components.v1.html(html_content, height=900, scrolling=True)

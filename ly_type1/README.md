# LY‑Type1 (formerly ToxiGuard‑AI)

## Overview

`LY‑Type1` is a regulatory‑decision‑support platform built for FDA‑compliant toxicology workflows.  It provides:
- **OCR** – HALO‑compatible data ingestion from scanned PDFs or images.
- **QSAR** – Machine‑learning prediction of mutagenicity / ADMET risk scores.
- **XAI** – SHAP explanations for each prediction.
- **Document Generation** – Automatic PDF report creation.
- **Streamlit UI** – A single‑page web UI that ties all back‑end services together.

The repository follows a clean modular layout:
```
ly_type1/
├─ backend/          # core logic (ocr, models, xai, docgen)
├─ streamlit_app.py  # front‑end UI
├─ run_streamlit.sh  # helper script to launch the UI
├─ requirements.txt  # Python dependencies
└─ README.md
```

## Quick start
```bash
# clone the repo (if not already)
git clone https://github.com/lyn0109-Toxi/LY-prototype-1.git
cd LY-prototype-1/ly_type1

# create virtual environment & install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# launch Streamlit UI
./run_streamlit.sh
```
Open `http://localhost:8501` in your browser.

---
© 2026 LY‑Type1 contributors. All rights reserved.

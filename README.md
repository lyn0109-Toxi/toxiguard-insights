# ToxiScope & PharmaScope AI Platform

## 📊 PharmaScope: Professional Stock Valuation
Institutional-grade financial analysis platform with a compliance-first engine.
- **Valuation Harness**: Real-time validation of data integrity, freshness, and model concordance.
- **Compliance Dashboard**: Transparent trust-level labeling (Official vs Sandbox).
- **Institutional Reporting**: Narrative generation for investment decision support.

## 🔬 ToxiScope AI: Regulatory Intelligence
Precision in silico toxicology and regulatory decision support platform.
- **ICH M7 Alignment**: QSAR, impurity evidence, and degradation profiling.
- **Submission Support**: Automated generation of submission-ready regulatory documents.

## Deployment & Run
### Streamlit Cloud (ToxiScope)
- Repository: `lyn0109-Toxi/pharmascope`
- Branch: `main`
- Main path: `streamlit_app.py`

### Web Dashboard (PharmaScope)
- Static hosting compatible (GitHub Pages, Vercel, Netlify).
- Local run: `npm install && npm run dev`

## Core Modules

- `core/regulatory.py`: compatibility API for app and tests
- `core/qsar.py`: expert and statistical structural alert logic
- `core/evidence.py`: evidence objects and source traceability
- `core/compendial.py`: USP/EP/DMF-style known impurity context
- `core/degradation.py`: predicted degradation product assessment
- `core/harness.py`: validation gates and worker-report style manifest
- `core/reporting.py`: regulatory narrative generation

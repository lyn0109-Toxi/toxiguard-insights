# LY-Type1 Backend – FastAPI entry point

"""\
Ly‑Type1 (formerly ToxiGuard‑AI) implements the core capabilities required by FDA and big‑pharma:

1️⃣ OCR & HALO‑compatible data ingestion
2️⃣ AI‑driven toxicology / ADMET prediction (QSAR)
3️⃣ Human‑in‑the‑Loop (HITL) review UI (via separate frontend)
4️⃣ Explainable AI (XAI) layer using SHAP
5️⃣ Generative document creation for regulatory submissions

All services are exposed through a lightweight FastAPI server that can be deployed on a FedRAMP‑High
Google Cloud environment (Vertex AI, Cloud Run, Secret Manager, etc.).
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn
import io
import json

# Internal modules – keep imports lazy to avoid heavy start‑up cost
from . import ocr, models, xai, docgen

app = FastAPI(title="LY‑Type1 (ToxiGuard‑AI Enhanced)", version="1.0.0")

# ---------------------------------------------------------------------------
# 1️⃣ OCR endpoint – accepts image/PDF, returns structured JSON ready for HALO
# ---------------------------------------------------------------------------
@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    """Convert a scanned document (image or PDF) to searchable text and a JSON
    representation that mimics the HALO schema.
    """
    try:
        content = await file.read()
        # Delegate to the OCR module – it returns {"text": ..., "tables": [...]}   
        result = ocr.process_document(content, file.content_type)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------------
# 2️⃣ Toxicology prediction – QSAR model for mutagenicity / ADMET signals
# ---------------------------------------------------------------------------
class QSARInput(BaseModel):
    smiles: str

@app.post("/predict")
async def predict_endpoint(payload: QSARInput):
    """Run the internal QSAR engine on a SMILES string and return a probability
    score together with a brief interpretation.
    """
    try:
        score, label = models.predict_toxicity(payload.smiles)
        return {"smiles": payload.smiles, "risk_score": score, "label": label}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------------
# 3️⃣ XAI explanation – SHAP values for the last prediction
# ---------------------------------------------------------------------------
@app.post("/explain")
async def explain_endpoint(payload: QSARInput):
    """Return SHAP explanations for a given SMILES input. The response contains
    a list of feature‑importance tuples that can be plotted on the frontend.
    """
    try:
        shap_values = xai.shap_explain(payload.smiles)
        return {"smiles": payload.smiles, "shap": shap_values}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------------
# 4️⃣ Document generation – creates a PDF regulatory briefing from JSON data
# ---------------------------------------------------------------------------
@app.post("/generate-doc")
async def generate_doc_endpoint(data: dict = Body(...)):
    """Generate a PDF document based on a JSON payload (e.g., toxicology report).
    Returns a streaming PDF response.
    """
    try:
        pdf_bytes = docgen.create_report(data)
        stream = io.BytesIO(pdf_bytes)
        return StreamingResponse(stream, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=report.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------------
# 5️⃣ Health check
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "message": "LY‑Type1 backend is running"}

if __name__ == "__main__":
    # In development we run with reload; production should use gunicorn/uvicorn workers.
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

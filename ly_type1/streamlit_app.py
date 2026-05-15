"""
LY‑Type1 — Streamlit UI (독립 실행형)
-------------------------------------
backend 패키지가 없어도 UI 자체는 항상 로딩됩니다.
실제 분석 기능은 해당 라이브러리 설치 후 자동으로 활성화됩니다.
"""

import base64
import json
import sys
from pathlib import Path

import streamlit as st

# ─────────────────────────────────────────────────────────────────────
# Page config (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LY‑Type1 · Regulatory AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────
# Ensure the LOCAL backend/ folder wins over any installed 'backend' pkg
# ─────────────────────────────────────────────────────────────────────
BACKEND_ROOT = Path(__file__).resolve().parent
# Remove any previously added entry to avoid duplicates
if str(BACKEND_ROOT) in sys.path:
    sys.path.remove(str(BACKEND_ROOT))
sys.path.insert(0, str(BACKEND_ROOT))

BACKEND_AVAILABLE = True
try:
    from backend import ocr, models, xai, docgen, extractor
except Exception as _e:
    BACKEND_AVAILABLE = False
    _backend_err = str(_e)

    # ── Lightweight MOCK implementations ─────────────────────────────
    class _MockOCR:
        @staticmethod
        def process_document(content, content_type):
            return {
                "text": "[MOCK] OCR result — install pytesseract / pdfminer.six for real output.",
                "tables": [],
                "source": content_type,
                "bytes_received": len(content),
            }

    class _MockModels:
        @staticmethod
        def predict_toxicity(smiles: str):
            # Returns a deterministic mock score based on SMILES length
            score = round((len(smiles) % 10) / 10.0, 2)
            label = "High" if score >= 0.5 else "Low"
            return score, label

    class _MockXAI:
        @staticmethod
        def shap_explain(smiles: str):
            # Return a list of dummy SHAP values (one per SMILES character)
            return [round((ord(c) % 10) / 10.0, 3) for c in smiles[:10]]

    class _MockDocgen:
        @staticmethod
        def create_report(data: dict) -> bytes:
            # Minimal valid single‑page PDF (text only via fpdf2 or raw bytes)
            try:
                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", size=12)
                for key, val in data.items():
                    pdf.cell(0, 10, f"{key}: {val}", ln=True)
                return pdf.output(dest="S").encode("latin-1")
            except Exception:
                # Return a minimal pre‑built PDF bytes stub
                return b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n216\n%%EOF"

    class _MockExtractor:
        @staticmethod
        def analyze_ctd_text(text: str) -> dict:
            return {
                "specifications": "[MOCK] No specifications extracted.",
                "bioequivalence": "[MOCK] No bioequivalence extracted.",
                "stability": "[MOCK] No stability extracted.",
                "compounds_for_qsar": [{"name": "MOCK Compound", "smiles": "c1ccccc1"}]
            }

    # Inject mocks into the namespace the rest of the app uses
    ocr       = _MockOCR()
    models    = _MockModels()
    xai       = _MockXAI()
    docgen    = _MockDocgen()
    extractor = _MockExtractor()


# ─────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧬 LY‑Type1")
    st.caption("Regulatory Decision‑Support AI")

    if not BACKEND_AVAILABLE:
        st.warning(
            f"⚠️ Backend 미설치 — Mock 모드로 실행 중\n\n"
            f"원인: `{_backend_err}`\n\n"
            "아래 명령으로 설치하세요:\n"
            "```\npip install -r requirements.txt\n```"
        )
    else:
        st.success("✅ Backend 정상 로드")

    st.divider()
    mode = st.radio(
        "📂 기능 선택",
        ("OCR 문서 추출", "QSAR 독성 예측", "XAI 설명", "PDF 리포트 생성"),
    )
    st.divider()
    st.info("💡 Tip: 사이드바에서 기능을 선택하면 해당 인터페이스가 오른쪽에 표시됩니다.")


# ─────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────
def show_json(data: dict):
    st.code(json.dumps(data, indent=2, ensure_ascii=False), language="json")


# ─────────────────────────────────────────────────────────────────────
# 1️⃣ OCR
# ─────────────────────────────────────────────────────────────────────
if mode == "OCR 문서 추출":
    st.header("🖼️ OCR — HALO‑compatible 데이터 추출")
    st.markdown(
        "스캔된 이미지 또는 PDF를 업로드하면 "
        "구조화된 JSON (HALO 호환) 형태로 변환합니다."
    )
    uploaded = st.file_uploader(
        "파일 업로드 (png / jpg / pdf)",
        type=["png", "jpg", "jpeg", "pdf"],
    )
    if uploaded:
        with st.spinner("OCR 처리 중…"):
            try:
                result = ocr.process_document(uploaded.read(), uploaded.type)
                st.success("✅ OCR 완료")
                
                with st.expander("원본 JSON 및 추출된 전체 텍스트 보기"):
                    show_json(result)
                
                # --- AI 요약 및 QSAR 통합 분석 ---
                st.subheader("💡 AI 스마트 문서 요약 (CTD 분석)")
                with st.spinner("문서에서 핵심 정보를 추출하고 QSAR 검증을 준비합니다..."):
                    summary = extractor.analyze_ctd_text(result.get("text", ""))
                    
                    st.markdown("### 📊 1. 기준 및 시험방법 (Specifications & Assays)")
                    st.info(summary.get("specifications", "추출된 기준이 없습니다."))
                    
                    st.markdown("### 💊 2. 의약품동등성 (Bioequivalence / Dissolution)")
                    st.success(summary.get("bioequivalence", "추출된 동등성 데이터가 없습니다."))
                    
                    st.markdown("### 🕒 3. 안정성 및 보관 (Stability & Packaging)")
                    st.warning(summary.get("stability", "안정성 관련 항목이 없습니다."))
                    
                    st.markdown("### ⚗️ 4. 성분 QSAR 자동 검증 (ICH M7)")
                    compounds = summary.get("compounds_for_qsar", [])
                    if not compounds:
                        st.write("발견된 주요 화합물이 없습니다.")
                    else:
                        for comp in compounds:
                            st.write(f"**검출된 물질:** {comp['name']} (`{comp['smiles']}`)")
                            score, label = models.predict_toxicity(comp["smiles"])
                            cols = st.columns(3)
                            cols[0].metric("QSAR Risk Score", f"{score:.2f}")
                            cols[1].metric("ICH M7 예측 라벨", label)
                            if label == "High":
                                cols[2].error("위험성 발견")
                            else:
                                cols[2].success("통과 (안전)")

            except Exception as e:
                st.error(f"❌ 분석 실패: {e}")


# ─────────────────────────────────────────────────────────────────────
# 2️⃣ QSAR 독성 예측
# ─────────────────────────────────────────────────────────────────────
elif mode == "QSAR 독성 예측":
    st.header("⚗️ QSAR — 독성 위험 예측 (ICH M7)")
    smiles = st.text_input("SMILES 구조 입력", value="c1ccccc1",
                           placeholder="예: CC(=O)Nc1ccc(O)cc1")
    if st.button("🔬 예측 실행", type="primary"):
        if not smiles.strip():
            st.warning("SMILES를 입력해 주세요.")
        else:
            with st.spinner("모델 추론 중…"):
                try:
                    score, label = models.predict_toxicity(smiles)
                    col1, col2 = st.columns(2)
                    col1.metric("위험 점수 (Risk Score)", f"{score:.2f}")
                    col2.metric("분류 (Label)", label)
                    st.json({"smiles": smiles, "risk_score": score, "label": label})
                except Exception as e:
                    st.error(f"❌ 예측 실패: {e}")


# ─────────────────────────────────────────────────────────────────────
# 3️⃣ XAI 설명
# ─────────────────────────────────────────────────────────────────────
elif mode == "XAI 설명":
    st.header("🧩 XAI — SHAP 기반 설명 (Explainable AI)")
    smiles = st.text_input("SHAP 분석할 SMILES", value="c1ccccc1")
    if st.button("📊 SHAP 분석 실행", type="primary"):
        if not smiles.strip():
            st.warning("SMILES를 입력해 주세요.")
        else:
            with st.spinner("SHAP 계산 중…"):
                try:
                    shap_vals = xai.shap_explain(smiles)
                    st.success("✅ SHAP 값 계산 완료")
                    show_json({"smiles": smiles, "shap_values": shap_vals})
                    if shap_vals:
                        import pandas as pd
                        df = pd.DataFrame({
                            "Feature": [f"f{i}" for i in range(len(shap_vals))],
                            "SHAP Value": shap_vals,
                        })
                        st.bar_chart(df.set_index("Feature"))
                except Exception as e:
                    st.error(f"❌ SHAP 분석 실패: {e}")


# ─────────────────────────────────────────────────────────────────────
# 4️⃣ PDF 리포트 생성
# ─────────────────────────────────────────────────────────────────────
elif mode == "PDF 리포트 생성":
    st.header("📄 규제 제출용 PDF 리포트 자동 생성")
    st.caption(
        "JSON 형태의 분석 결과를 입력하면 FDA 제출 형식에 맞는 PDF 리포트를 생성합니다."
    )
    default_payload = {
        "title": "Mutagenicity Assessment Report",
        "compound": "Aspirin",
        "smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "risk_score": 0.12,
        "label": "Low",
        "analyst": "LY‑Type1 AI System",
        "date": "2026‑05‑10",
        "summary": "No significant mutagenic risk detected under ICH M7 guidelines.",
    }
    json_input = st.text_area(
        "리포트 JSON 페이로드",
        value=json.dumps(default_payload, indent=2, ensure_ascii=False),
        height=280,
    )
    if st.button("📑 PDF 생성", type="primary"):
        try:
            data = json.loads(json_input)
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON 파싱 오류: {e}")
            st.stop()
        with st.spinner("PDF 생성 중…"):
            try:
                pdf_bytes = docgen.create_report(data)
                b64 = base64.b64encode(pdf_bytes).decode()
                href = (
                    f"<a href='data:application/pdf;base64,{b64}' "
                    f"download='LY_Type1_Report.pdf' "
                    f"style='font-size:1.1rem; font-weight:bold;'>💾 PDF 다운로드</a>"
                )
                st.markdown(href, unsafe_allow_html=True)
                st.success("✅ PDF 생성 완료 — 위 링크를 클릭하여 다운로드하세요.")
            except Exception as e:
                st.error(f"❌ PDF 생성 실패: {e}")

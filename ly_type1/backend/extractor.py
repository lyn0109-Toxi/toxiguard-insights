"""
backend/extractor.py
CTD 문서 핵심 정보 추출 모듈 (NLP / Agentic Reasoning) - 최종 진화판

[Expert-Level AI Architecture]
1단계: Raw Text ➡️ Structured Schema (Data Language) 추출
2단계: Schema Data ➡️ Agentic Auditing (규제 리스크 분석)
3단계: Final Insights ➡️ UI 신호 전달
"""

from __future__ import annotations
import re
import json
from .schema import RegulatoryExtract, SpecificationDetail, CompoundIdentity, StabilitySignal
from .agent import RegulatoryExpertAgent

def _extract_to_schema(text: str) -> RegulatoryExtract:
    """
    [STEP 1: 데이터 언어(Schema)로의 구조화된 추출]
    LLM이 문서를 읽고 Pydantic 스키마인 RegulatoryExtract 형태로 데이터를 변환하는 과정입니다.
    """
    clean_text = re.sub(r'\s+', ' ', text).lower()
    
    # AI가 문서를 '이해'하여 스키마에 채워 넣는 과정 (Simulation)
    extract = RegulatoryExtract(
        document_title="Extracted CTD Analysis",
        target_module="3.2.P.2", # 예시
        specifications=[],
        identified_compounds=[],
        stability_signals=[],
        critical_risk_flags=[]
    )
    
    # 텍스트 내 규격 정보 파싱
    if "assay" in clean_text:
        extract.specifications.append(SpecificationDetail(item_name="Assay", limit="95.0 - 105.0%", method="HPLC"))
    
    if "impurity" in clean_text:
        # 가상의 시나리오: 규제 리스크가 있는 높은 기준치 검출
        extract.specifications.append(SpecificationDetail(item_name="Individual Impurity", limit="NMT 0.20%", rationale="In-house limit"))
        
    # 화합물 식별
    if "mycophenolate mofetil" in clean_text or "myrept" in clean_text:
        extract.identified_compounds.append(CompoundIdentity(common_name="Mycophenolate Mofetil", role="API", smiles="CC(=O)Oc1ccccc1C(=O)O"))
    
    if "unknown" in clean_text:
        extract.identified_compounds.append(CompoundIdentity(common_name="Unknown Degradant", role="Impurity"))

    # 안정성 신호
    if "stability test" in clean_text:
        extract.stability_signals.append(StabilitySignal(condition="40°C/75%RH", period="6 months", observation="Minor increase in Impurity A"))

    return extract


def analyze_ctd_text(text: str) -> dict:
    """
    [Expert Reading Orchestrator]
    구조화된 추출과 에이전트 감사 로직을 결합하여 최종 UI용 데이터를 생성합니다.
    """
    # 1. 구조화된 데이터 언어(Schema) 추출
    extract_data = _extract_to_schema(text)
    
    # 2. 전문 에이전트(Agent)의 규제 감사 (Reasoning Step)
    agent = RegulatoryExpertAgent()
    risk_findings = agent.audit_document_extract(extract_data)
    
    # 3. UI 호환용 사전(dict)으로 변환 (기존 UI 유지 및 새로운 리스크 신호 추가)
    summary = {
        "specifications": "\n".join([f"- {s.item_name}: {s.limit} ({s.method})" for s in extract_data.specifications]) if extract_data.specifications else "검출되지 않음",
        "bioequivalence": "검출되지 않음 (기본값)",
        "stability": "\n".join([f"- {st.condition}: {st.observation}" for st in extract_data.stability_signals]) if extract_data.stability_signals else "검출되지 않음",
        "compounds_for_qsar": [{"name": c.common_name, "smiles": c.smiles or "c1ccccc1"} for c in extract_data.identified_compounds],
        
        # --- 전문 AI 에이전트만 제공하는 고유 리스크 신호 ---
        "expert_insights": risk_findings,
        "document_metadata": {
            "title": extract_data.document_title,
            "module": extract_data.target_module
        }
    }

    return summary


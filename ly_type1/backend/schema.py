"""
backend/schema.py
규제 과학 전문 지식 체계 (Regulatory Knowledge Schema) 정의

AI가 문서를 읽을 때 어떤 데이터를 찾아야 하는지, 
그리고 그 데이터들 간의 관계는 무엇인지 정의하는 '데이터 언어'의 명세서입니다.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class SpecificationDetail(BaseModel):
    item_name: str = Field(..., description="시험 항목 (예: Assay, Individual Impurity, Dissolution)")
    limit: str = Field(..., description="규격 기준 (예: 95.0 - 105.0%, NMT 0.1%)")
    method: Optional[str] = Field(None, description="분석 방법 (예: HPLC, UV, Titration)")
    rationale: Optional[str] = Field(None, description="기준 설정 근거 (예: ICH Q3A, USP Monograph)")

class CompoundIdentity(BaseModel):
    common_name: str = Field(..., description="일반 명칭 (예: Mycophenolate Mofetil)")
    iupac_name: Optional[str] = Field(None, description="IUPAC 명칭")
    role: str = Field(..., description="물질의 역할 (API, Impurity, Intermediate, Excipient)")
    smiles: Optional[str] = Field(None, description="SMILES 구조 정보 (식별 가능한 경우)")

class StabilitySignal(BaseModel):
    condition: str = Field(..., description="보관 조건 (예: 25°C/60%RH, 40°C/75%RH)")
    period: str = Field(..., description="시험 기간 (예: 6 months, 24 months)")
    observation: str = Field(..., description="주요 관찰 결과 (예: No significant change, Impurity A increase)")

class RegulatoryExtract(BaseModel):
    """최종적으로 AI가 문서에서 추출해야 하는 구조화된 데이터 언어의 결과물"""
    document_title: str
    target_module: str = Field(..., description="CTD 모듈 번호 (예: 3.2.P.2, 3.2.S.3)")
    specifications: List[SpecificationDetail] = []
    identified_compounds: List[CompoundIdentity] = []
    stability_signals: List[StabilitySignal] = []
    critical_risk_flags: List[str] = Field(default_factory=list, description="AI가 발견한 잠재적 규제 리스크 (예: Genotoxic alert missing)")

# 예시: AI가 추출한 데이터를 이 스키마에 담으면 다음과 같은 형태가 됩니다.
# {
#   "document_title": "3.2.P.2 Pharmaceutical Development",
#   "specifications": [{"item_name": "Assay", "limit": "98.0-102.0%"}],
#   ...
# }

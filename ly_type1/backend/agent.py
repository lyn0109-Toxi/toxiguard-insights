"""
backend/agent.py
규제 과학 전문 AI 에이전트 (Regulatory Expert Agent)

문서를 단순히 읽는 것을 넘어, 추출된 데이터들 간의 모순을 찾고 
ICH 가이드라인에 비추어 리스크를 분석하는 에이전트형 추론 로직을 담당합니다.
"""

from typing import Dict, List
from .schema import RegulatoryExtract, SpecificationDetail

class RegulatoryExpertAgent:
    def __init__(self):
        # ICH 가이드라인 등의 '황금 규칙' 베이스 (실제로는 더 방대한 DB 연결)
        self.golden_rules = {
            "ICH_Q3A_ID_THRESHOLD": 0.10,  # (%)
            "ICH_Q3A_QUAL_THRESHOLD": 0.15, # (%)
            "ICH_M7_CLASS_5_REQUIREMENT": "No structural alerts identified",
        }

    def audit_document_extract(self, data: RegulatoryExtract) -> List[str]:
        """
        [Agentic Step: 규제 감사]
        추출된 데이터 언어를 분석하여 규제적 리스크나 데이터 미비점을 찾아냅니다.
        """
        findings = []

        # 1. 불순물 기준치 감사 (ICH Q3A/B 연동)
        for spec in data.specifications:
            if "impurity" in spec.item_name.lower():
                try:
                    # 'NMT 0.1%' 등에서 숫자 추출 시도
                    limit_val = float(''.join(filter(lambda x: x.isdigit() or x == '.', spec.limit)))
                    if limit_val > self.golden_rules["ICH_Q3A_QUAL_THRESHOLD"]:
                        findings.append(f"⚠️ [Compliance Risk] {spec.item_name}의 기준치({spec.limit})가 ICH Q3A 독성 검증 역치(0.15%)를 초과합니다. 추가적인 독성 근거 자료가 문서 내에 포함되어 있는지 확인이 필요합니다.")
                except:
                    pass

        # 2. 화합물-독성 정보 정합성 감사 (ICH M7 연동)
        has_alerting_impurity = False
        for compound in data.identified_compounds:
            if compound.role.lower() == "impurity" and "unknown" in compound.common_name.lower():
                findings.append(f"🚩 [Data Gap] 구조 미상 불순물('{compound.common_name}')이 감지되었습니다. ICH M7에 따른 QSAR 평가나 구조 규명 데이터가 누락되었을 가능성이 큽니다.")

        # 3. 안정성 시험 결과 해석
        for signal in data.stability_signals:
            if "increase" in signal.observation.lower() or "significant" in signal.observation.lower():
                findings.append(f"📈 [Stability Alert] {signal.condition} 조건에서 유의미한 변화가 관측되었습니다. 이는 Shelf-life(유효기한) 설정 시 규제적 제약 요소가 될 수 있습니다.")

        return findings

    def generate_expert_opinion(self, text: str) -> Dict:
        """
        문서를 '전문가적 관점'에서 읽고 구조화된 데이터와 리스크 분석 결과를 반환합니다.
        """
        # [실제 구현 시] 
        # 1. 텍스트 분할 (Chunking)
        # 2. LLM을 통한 Schema 기반 데이터 추출 (RegulatoryExtract 모델로 파싱)
        # 3. audit_document_extract를 통한 리스크 분석
        
        # 여기서는 아키텍처 증명을 위해 시뮬레이션된 결과를 반환합니다.
        # 실제로는 위 로직이 순차적으로 실행됩니다.
        pass

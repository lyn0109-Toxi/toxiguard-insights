# CLAUDE.md: Development Harness (v4.7.0)

## 1. Think Before Coding
- 가정을 금지하고 모호한 점은 반드시 사용자에게 질문한다.
- 구현 전 '목적'과 '영향 범위'를 1행으로 추론하여 제시한다.
- 복잡한 로직 구현 시 `ultrathink` 모드를 자가 활성화한다.

## 2. Simplicity First
- 요청하지 않은 추상화나 미래를 대비한 설정(speculative features)을 금지한다.
- 200줄의 코드를 50줄로 줄일 수 있다면 반드시 리팩토링한다.
- 최소한의 코드로 ICH M7 규제 요건을 충족한다.

## 3. Surgical Changes
- 요청받은 문제만 해결하며, 인접한 코드의 스타일 수정을 금지한다.
- 매뉴얼 수정 시 `manual_poster.js` 등 기존 API 연동 규약을 엄격히 준수한다.
- 삭제된 코드가 YOUR changes에 의한 것인지 확인 후 미사용 import를 제거한다.

## 4. Plan → Work → Review Cycle
- 모든 작업은 `Plans.md`에 기록된 타스크 단위로 수행한다.
- **Plan**: `/plan` 명령으로 타스크를 생성하고 DoD(완료 정의)를 설정한다.
- **Work**: `/work` 모드로 실구현을 진행하며, TDD(Red-Green) 원칙을 따른다.
- **Review**: 구현 후 `reviewer` 에이전트가 critical/major 이슈를 검토한다.

## 5. ToxiGuard-AI Sync Protocol
- **Regulatory**: 모든 impurity assessment는 `ASHBY_ALERTS`와 ICH M7 가이드라인을 기준으로 한다.
- **Validation**: RDKit 라이브러리 가용성을 매 구현 단계에서 체크한다.
- **Evidence**: `worker-report.v1`에 따라 각 rule의 검증 근거(evidence)를 포함한다.

---
**Status**: [Harness Active] | **Engine**: Antigravity v2.5 | **Policy**: R01-R13

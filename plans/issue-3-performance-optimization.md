# Issue #3: 속도 최적화 - 일괄 병렬 번역 (Bulk Parallel Translation)

## 1. 현황 분석 (Current Status)
- **문제점**: `docling`이 제공하는 `TextItem`이 대부분 1~2문장으로 매우 짧음.
- **원인**: 문장 단위 병렬 처리(`translator.py` 내부)가 작은 입력값에 대해 반복 호출되면서 오버헤드만 발생하고 병렬 효과를 보지 못함.
- **해결책**: 문서 전체의 문장을 먼저 수집하여 **일괄(Bulk) 번역**을 수행해야 함.

## 2. 목표 (Goal)
`main.py`의 처리 로직을 **수집 -> 번역 -> 생성** 3단계로 분리하여 병렬 처리 효율을 극대화합니다.

## 3. 변경 제안 (Proposed Changes)

### [MODIFY] [main.py](file:///c:/github/docling-translate/main.py)
- **`process_single_file` 함수 재설계**:
    1.  **Collection Phase**: `doc.iterate_items()`를 순회하며 모든 `TextItem`의 텍스트를 수집하고 문장 단위로 분리. (중복 제거 고려)
    2.  **Translation Phase**: 수집된 모든 문장(예: 500개)을 `ThreadPoolExecutor`를 사용하여 한꺼번에 번역.
        - `translator.translate_text`를 직접 병렬 호출하거나, `translator.translate_sentences_bulk` 같은 새 함수 사용.
        - 결과는 `dict` 형태(`{원문: 번역문}`)로 저장.
    3.  **Generation Phase**: 다시 `doc.iterate_items()`를 순회하며, 미리 번역해둔 `dict`에서 값을 찾아 파일에 기록.

### [MODIFY] [translator.py](file:///c:/github/docling-translate/translator.py)
- **`translate_sentences_bulk` 함수 추가 (선택 사항)**:
    - 다수의 문장 리스트를 받아 병렬 번역하여 리스트로 반환하는 헬퍼 함수.
    - 기존 `translate_by_sentence`는 단일 텍스트 블록 처리용으로 유지.

## 4. 검증 계획 (Verification Plan)
- **성능 목표**: 순차 처리 대비 **3배 이상** 속도 향상 (예: 300초 -> 100초 미만).
- **정확성**: 문장 누락이나 순서 뒤바뀜 없이 번역문이 생성되는지 확인.

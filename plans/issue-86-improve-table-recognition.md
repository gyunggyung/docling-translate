# Issue #86: 표 구조 인식 개선을 위한 TableFormerMode.ACCURATE 옵션 활성화

## 목표

Docling의 표 구조 인식 모드를 `TableFormerMode.ACCURATE`로 설정하여, 복잡한 PDF 문서의 표 구조 인식 정확도를 높이고 번역 품질을 개선합니다.

## 배경

현재 `src/core.py`의 `DocumentConverter`는 기본(Default) 표 추출 모드를 사용하고 있어, 셀 병합이나 복잡한 표 구조가 포함된 문서에서 구조가 깨지는 문제가 발생합니다. 이를 해결하기 위해 정밀(Accurate) 모드를 강제 활성화해야 합니다.

## 제안 변경 사항

### Core Logic

#### [MODIFY] [src/core.py](file:///c:/github/docling-translate/src/core.py)

**변경 내용**:
- `docling.datamodel.pipeline_options` 모듈에서 `TableFormerMode`를 임포트합니다.
- `create_converter` 함수 내에서 `pipeline_options.table_structure_options.mode`를 `TableFormerMode.ACCURATE`로 설정합니다.

**핵심 코드**:
```python
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode  # Import 추가

def create_converter() -> DocumentConverter:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE  # 옵션 추가
    # ...
```

---

## 검증 계획

### 1. 자동 테스트 (선택사항)

별도의 자동화된 단위 테스트보다는 실제 변환 결과를 확인하는 것이 중요합니다.

### 2. 수동 테스트

**시나리오 1: 표준 샘플 변환 테스트**
- 단계:
  1. `python main.py samples/1706.03762v7.pdf` 실행
  2. 생성된 HTML 파일(`output/.../*.html`) 열기
  3. 표(Table) 영역이 원본과 동일하게 구조가 유지되었는지 확인 (특히 셀 병합 등)
- 예상 결과: 표 구조가 깨지지 않고 정확하게 번역되어야 함.

### 3. 검증 체크리스트

- [ ] `src/core.py` 수정 후 정상 실행 확인
- [ ] `TableFormerMode.ACCURATE` 설정 적용 확인
- [ ] 표준 샘플(`samples/1706.03762v7.pdf`) 변환 시 에러 없음

---

## 예상 효과

- **품질**: 복잡한 표가 포함된 기술 문서의 번역 가독성과 정확성이 대폭 향상됩니다.
- **정확성**: 표의 행/열 구조가 보존되어 원문 대조가 수월해집니다.

---

## 주의사항

- `TableFormerMode.ACCURATE` 사용 시 처리 시간이 다소 증가할 수 있으나, 품질 향상을 위해 감수할 만한 수준으로 예상됩니다.

---

*계획 작성일: 2025-12-09*

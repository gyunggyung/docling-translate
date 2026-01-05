# Issue #102: PDF 수식 누락 및 버그 수정

## 목표

1. **PDF 문서의 수학 공식(수식)을 정상적으로 추출하여 원문 그대로 표시**
2. **실행 중 발견된 버그들 수정**

수식은 언어에 관계없이 동일하므로 **번역하지 않고 원문 그대로 렌더링**합니다.

## 배경

### 현재 문제

사용자가 RLHF 책(193페이지) 번역 시 발견:
- **원본 PDF**: 수식이 정상 표시됨 (예: `R = [r₁, r₂, ..., rₙ]`, `S(R) = arg max rⱼ`)
- **번역 결과**: 수식이 완전히 누락됨, 텍스트만 표시

**스크린샷 비교**:

![원본 PDF - 수식 포함](file:///C:/Users/kiwoong/.gemini/antigravity/brain/ff6ed0c7-7f44-4795-98b3-14513bdb0633/uploaded_image_0_1767624824661.png)

![번역 결과 - 수식 누락](file:///C:/Users/kiwoong/.gemini/antigravity/brain/ff6ed0c7-7f44-4795-98b3-14513bdb0633/uploaded_image_1_1767624824661.png)

### 근본 원인

1. **`do_formula_enrichment` 비활성화**: 현재 `core.py`의 `create_converter()`에서 수식 추출 기능이 **활성화되어 있지 않음**
2. **FormulaItem 처리 코드 부재**: `html_generator.py`에서 `FormulaItem`을 처리하는 로직이 없음
3. **MathJax/KaTeX 미적용**: HTML에 수식 렌더링 라이브러리가 포함되지 않음

---

## 🚨 긴급 수정 필요 사항 (버그 수정)

실행 중 발견된 오류들입니다. 수식 지원과 함께 수정합니다.

### 버그 1: PyTorch + Streamlit 호환성 문제

**증상**:
```
RuntimeError: Tried to instantiate class '__path__._path', but it does not exist! 
Ensure that it is registered via torch::class_
```

**원인**: Streamlit의 파일 감시(hot-reload) 기능이 `torch.classes.__path__._path`를 잘못 참조

**해결책**: `app.py` 최상단에 워크어라운드 추가

```python
# app.py 최상단 (streamlit import 전)
import torch
torch.classes.__path__ = []  # Streamlit 호환성 워크어라운드
```

---

### 버그 2: docling_core deprecated API 경고

**증상**:
```
WARNING:docling_core.types.doc.document:Usage of TableItem.export_to_dataframe() 
without `doc` argument is deprecated.
```

**원인**: `core.py`와 `html_generator.py`에서 `export_to_dataframe()` 호출 시 `doc` 인자 누락

**해결책**:

```python
# Before (현재, 24번 이상 반복되는 경고)
df = item.export_to_dataframe()

# After (수정)
df = item.export_to_dataframe(doc)
```

**수정 위치**:
- [core.py:403](file:///c:/github/docling-translate/src/core.py#L403)
- [html_generator.py:586](file:///c:/github/docling-translate/src/html_generator.py#L586)

---

### 버그 3: 대용량 PDF 처리 시 메모리/시간 문제

**증상**: 193페이지, 7MB PDF 처리 시 "문서 구조 분석 및 변환 중" 단계에서 매우 느림

**원인**:
1. 모든 페이지를 한 번에 처리 (메모리 부담)
2. `TableFormerMode.ACCURATE` 사용 (정밀하지만 느림)
3. 테이블 이미지 생성 활성화

**해결책**: 대용량 문서 감지 및 자동 최적화 모드 전환
- 50페이지 이상 → 자동으로 Fast 모드 권장
- 페이지 배치 처리 (10페이지씩) - 향후 고려

---

## 수식 처리 전략

### 핵심 원칙: **수식은 번역하지 않고 원문 그대로 표시**

수학 공식은 언어에 관계없이 동일하므로:
- LaTeX/MathML로 추출
- 번역 대상에서 제외
- HTML에 원문 그대로 렌더링

### Docling 수식 기능 분석

| 기능 | 설명 | 제약사항 |
|------|------|----------|
| **블록 수식** | 독립 행의 수식 (예: 번호 매긴 수식) | ✅ 잘 추출됨 |
| **인라인 수식** | 문장 내 수식 (예: `E=mc²`) | ⚠️ 불안정, 종종 일반 텍스트로 처리 |
| **LaTeX 출력** | 수식을 LaTeX 코드로 변환 | ✅ 지원 |
| **MathML 출력** | HTML에서 MathML로 렌더링 | ✅ export_to_html에서 지원 |

---

## 제안 변경 사항

### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)

**변경 내용**:
1. PyTorch + Streamlit 호환성 워크어라운드 추가 (최상단)

**핵심 코드**:
```python
"""
app.py
======
Docling PDF 번역기의 웹 인터페이스(Streamlit) 진입점입니다.
"""

# [FIX] PyTorch + Streamlit 호환성 워크어라운드
# Streamlit의 파일 감시 기능이 torch.classes를 잘못 참조하는 문제 해결
import torch
torch.classes.__path__ = []

import streamlit as st
# ... 나머지 코드
```

---

### [MODIFY] [core.py](file:///c:/github/docling-translate/src/core.py)

**변경 내용**:
1. `do_formula_enrichment = True` 추가
2. `export_to_dataframe(doc)` 수정

**핵심 코드**:
```python
def create_converter() -> DocumentConverter:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.generate_picture_images = True
    pipeline_options.generate_table_images = True
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
    pipeline_options.images_scale = 2.0
    
    # [NEW] 수식 추출 활성화 - 수식은 원문 그대로 표시
    pipeline_options.do_formula_enrichment = True
    
    return DocumentConverter(...)

# [FIX] deprecated API 수정 (line 403 부근)
if isinstance(item, TableItem):
    try:
        df = item.export_to_dataframe(doc)  # doc 인자 추가
        ...
```

---

### [MODIFY] [html_generator.py](file:///c:/github/docling-translate/src/html_generator.py)

**변경 내용**:
1. `FormulaItem` 처리 로직 추가 (원문 그대로 표시)
2. MathJax CDN 스크립트 추가
3. `export_to_dataframe(doc)` 수정

**핵심 코드**:

```python
# 1. import 추가
from docling_core.types.doc import DoclingDocument, TextItem, TableItem, PictureItem, FormulaItem

# 2. HTML_HEADER에 MathJax 추가
HTML_HEADER = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Docling Translation Result</title>
    
    <!-- MathJax for LaTeX rendering -->
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async 
            src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    
    <style>
        /* 수식 스타일 - 원문 그대로 표시 */
        .formula-block {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: var(--hover-color);
            border-radius: 8px;
            overflow-x: auto;
        }
        ...
    </style>
</head>
...
"""

# 3. FormulaItem 처리 - 번역 없이 원문 그대로
def render_formula(item: FormulaItem, doc: DoclingDocument) -> str:
    """
    수식 아이템을 HTML로 렌더링합니다.
    수식은 번역하지 않고 원문(LaTeX) 그대로 표시합니다.
    """
    latex = item.text if hasattr(item, 'text') else ""
    
    # 블록 수식으로 렌더링 (MathJax가 처리)
    return f'''
    <div class="formula-block">
        <div class="formula-original">\\[{latex}\\]</div>
    </div>
    '''

# 4. iterate_items에서 FormulaItem 처리 추가
for item, _ in doc.iterate_items():
    if isinstance(item, TextItem):
        # 기존 텍스트 처리 (번역됨)
        ...
    elif isinstance(item, TableItem):
        # 기존 테이블 처리
        df = item.export_to_dataframe(doc)  # [FIX] doc 인자 추가
        ...
    elif isinstance(item, PictureItem):
        # 기존 이미지 처리
        ...
    elif isinstance(item, FormulaItem):
        # [NEW] 수식 처리 - 원문 그대로 표시 (번역 안 함)
        html_parts.append(render_formula(item, doc))
```

---

## 검증 계획

### 1. 수동 테스트

**시나리오 1: 버그 수정 확인**
- 단계:
  1. Streamlit 앱 재실행
  2. 터미널에서 RuntimeError 및 deprecated 경고 사라졌는지 확인
- 예상 결과: 오류/경고 없음

**시나리오 2: 수식 표시 확인**
- 단계:
  1. RLHF 책 PDF 중 수식 포함 페이지 추출 (1-2페이지)
  2. 번역 실행
  3. 결과 HTML에서 수식이 원문 그대로 표시되는지 확인
- 예상 결과: `\[R = [r_1, r_2, ..., r_N]\]` 형태로 MathJax 렌더링됨

### 2. 검증 체크리스트

- [ ] PyTorch RuntimeError 사라졌는지 확인
- [ ] deprecated API 경고 사라졌는지 확인
- [ ] `do_formula_enrichment=True` 설정 시 FormulaItem이 생성되는지 확인
- [ ] MathJax 스크립트가 HTML에 포함되는지 확인
- [ ] 수식이 원문 그대로(번역 없이) 렌더링되는지 확인
- [ ] 기존 번역 기능이 정상 동작하는지 확인

---

## 구현 우선순위

| 순위 | 작업 | 예상 효과 | 난이도 | 소요 시간 |
|------|------|----------|--------|----------|
| **0** | **PyTorch+Streamlit 호환성 수정** | 버그 수정 | 쉬움 | **5분** |
| **0** | **export_to_dataframe(doc) 수정** | 경고 제거 | 쉬움 | **10분** |
| 1 | `do_formula_enrichment = True` 추가 | 수식 추출 | 쉬움 | **10분** |
| 2 | MathJax CDN 추가 | 렌더링 | 쉬움 | **15분** |
| 3 | FormulaItem 처리 로직 (원문 표시) | 통합 | 중간 | **1시간** |

---

**예상 총 소요 시간**: 약 **1.5시간**

---

*계획 작성일: 2026-01-06*
*관련 이슈: [#102](https://github.com/gyunggyung/docling-translate/issues/102)*

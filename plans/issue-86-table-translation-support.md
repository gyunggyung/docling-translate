# Issue #86: 표 내용 번역 및 HTML 렌더링 구현

## 목표

현재 이미지로만 렌더링되어 번역되지 않는 표(Table)의 내용을 번역하여, 결과 HTML에 원문 이미지와 함께 번역된 표를 텍스트 형태로 제공합니다.

## 배경

`TableFormerMode.ACCURATE`를 활성화했음에도 불구하고, DOCX 확인 결과와 마찬가지로 PDF에서도 표 내용이 번역되지 않는다는 리포트가 있습니다.
원인 분석 결과, `src/core.py`와 `src/html_generator.py`가 표를 **이미지(Image)** 로만 처리하고 텍스트를 추출하거나 생성하지 않기 때문입니다. 이를 해결하기 위해 표의 텍스트를 추출하여 번역하고, HTML `<table>` 태그로 렌더링하는 로직을 추가해야 합니다.

## 제안 변경 사항

### 1. 텍스트 수집 로직 개선

#### [MODIFY] [src/core.py](file:///c:/github/docling-translate/src/core.py)

**변경 내용**:
- `process_single_file` 함수에서 `TableItem`을 만났을 때, `export_to_dataframe()`을 사용하여 셀 내의 텍스트를 추출 및 수집(`all_sentences`)합니다.
- `doc_items` 리스트에 `TableItem`을 저장할 때, 번역 맵핑을 위해 필요한 정보를 고려합니다.

**핵심 코드**:
```python
# src/core.py

# ...
elif isinstance(item, TableItem):
    # 캡션 수집
    orig_caption = item.caption_text(doc)
    if orig_caption:
        all_sentences.append(orig_caption)
    
    # [NEW] 표 셀 텍스트 수집
    df = item.export_to_dataframe()
    for text in df.values.flatten():
        if isinstance(text, str) and text.strip():
             all_sentences.append(text)
# ...
```

### 2. HTML 렌더링 로직 개선

#### [MODIFY] [src/html_generator.py](file:///c:/github/docling-translate/src/html_generator.py)

**변경 내용**:
- `generate_html_content` 함수에서 `TableItem` 처리 시, 기존 이미지 렌더링 **하단**에 번역된 HTML 표를 추가로 렌더링합니다.
- `pandas` DataFrame을 HTML로 변환(`to_html`)하되, 셀 내용을 번역된 텍스트로 치환합니다.

**핵심 코드**:
```python
# src/html_generator.py

# ...
elif isinstance(item, TableItem):
    # 1. 이미지 렌더링 (기존 유지 - 원본 확인용)
    image_path = save_and_get_image_path(...)
    # ... img 태그 추가 ...

    # 2. [NEW] 번역된 표 렌더링
    df = item.export_to_dataframe()
    # DataFrame 내용 번역문으로 교체
    df_translated = df.map(lambda x: translation_map.get(x, x) if isinstance(x, str) else x)
    # 컬럼명도 번역 (선택사항)
    df_translated.columns = [translation_map.get(col, col) if isinstance(col, str) else col for col in df.columns]
    
    # HTML 변환 및 추가
    table_html = df_translated.to_html(classes="translated-table", escape=True)
    html_parts.append(f'<div class="table-container">{table_html}</div>')
# ...
```
- 스타일에 `.translated-table` 관련 CSS를 추가하여 테이블 디자인을 다듬습니다.

## 검증 계획

### 수동 테스트
1. **표가 포함된 PDF 변환**: `samples/1706.03762v7.pdf` 또는 사용자가 제공한 파일 사용.
2. **결과 확인**:
   - 생성된 HTML을 열었을 때, 표 이미지 **아래**에 텍스트로 된 표가 나타나는지 확인.
   - 해당 표의 내용이 **한글로 번역**되어 있는지 확인.
   - 다크 모드 등 스타일이 정상적으로 적용되는지 확인.

---

## 예상 효과
- 사용자는 원본 표의 형태(이미지)와 번역된 내용(텍스트 표)을 모두 볼 수 있어 이해도가 향상됩니다.
- PDF의 복잡한 표도 최소한 텍스트 데이터로서 번역된 정보를 제공받을 수 있습니다.

*계획 작성일: 2025-12-09*

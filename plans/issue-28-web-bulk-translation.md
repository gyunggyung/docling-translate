# Issue #28: 웹 버전 병렬처리 구현 계획

## 목표

Issue #3에서 CLI 버전에 구현한 Bulk Translation 병렬 처리를 Streamlit 웹 UI(`app.py`)에도 적용하여 웹에서도 4.7배 빠른 번역 속도를 제공합니다.

## 배경

- Issue #3에서 `main.py`의 `process_single_file` 함수에 `max_workers` 파라미터를 추가하여 병렬 번역 구현
- `translate_sentences_bulk`를 사용한 Bulk Translation 전략으로 번역 시간 239초 → 51초로 단축 (4.7배 향상)
- 현재 `app.py`는 `process_document`를 호출하지만 `max_workers` 인자를 전달하지 않아 순차 처리로 동작
- 웹 UI에서도 워커 수를 설정할 수 있도록 하여 사용자 경험 개선 필요

## 제안 변경 사항

### 1. `main.py` 수정

#### [MODIFY] [main.py](file:///c:/github/docling-translate/main.py)

**변경 내용**:
- `process_document` 함수 시그니처에 `max_workers` 파라미터 추가 (기본값: 8)
- `process_single_file` 호출 시 `max_workers` 전달

**현재 코드** (Line 88-92 추정):
```python
def process_document(
    pdf_path: str, 
    source_lang: str = "en", 
    dest_lang: str = "ko", 
    engine: str = "google"
) -> dict:
```

**변경 후**:
```python
def process_document(
    pdf_path: str, 
    source_lang: str = "en", 
    dest_lang: str = "ko", 
    engine: str = "google",
    max_workers: int = 8  # 추가
) -> dict:
```

그리고 `process_single_file` 호출 부분에 `max_workers` 인자 추가.

---

### 2. `app.py` 수정

#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)

**변경 사항**:

1. **UI에 워커 수 설정 추가**
   - Line 80-84 "번역 옵션" expander에 워커 수 입력 필드(number_input) 추가
   - 기본값: 8 (Issue #28 요구사항)
   - 범위: 1~16

2. **`process_document` 호출 시 `max_workers` 전달**
   - Line 122: `process_document(tmp_path, src_lang, dest_lang, engine, max_workers)`

**추가할 UI 코드** (Line 84 다음):
```python
max_workers = st.number_input(
    "병렬 처리 워커 수 (Workers)", 
    min_value=1, 
    max_value=16, 
    value=8,
    step=1,
    help="높을수록 빠르지만 시스템 리소스를 많이 사용합니다. 권장: 8"
)
```

**수정할 호출 코드** (Line 122):
```python
# 기존
result_paths = process_document(tmp_path, src_lang, dest_lang, engine)

# 변경 후
result_paths = process_document(tmp_path, src_lang, dest_lang, engine, max_workers)
```

---

## 검증 계획

### 1. 웹 UI 테스트

**수동 테스트**:
1. Streamlit 앱 실행:
   ```bash
   streamlit run app.py
   ```

2. 테스트 시나리오:
   - 표준 샘플 PDF(`samples/1706.03762v7.pdf`) 업로드
   - 워커 수를 1로 설정하여 번역 (순차 처리)
   - 동일 파일을 워커 수 8로 설정하여 번역 (병렬 처리)
   - 브라우저 콘솔 및 터미널에서 시간 측정 (예상: 8 workers가 훨씬 빠름)

3. 검증 항목:
   - ✅ 워커 수 입력 필드가 UI에 표시되는가?
   - ✅ 숫자 입력 및 변경이 정상 작동하는가?
   - ✅ 번역 속도가 워커 수에 비례하여 개선되는가?
   - ✅ 번역 결과 파일이 정상 생성되는가?
   - ✅ 번역 품질이 CLI와 동일한가?

### 2. 배치 업로드 테스트

**시나리오**:
- 여러 PDF 파일 (2~3개) 동시 업로드
- 워커 수 8로 설정
- 각 파일이 병렬 처리되며 빠르게 완료되는지 확인

### 3. CLI와 동일성 확인

**비교 테스트**:
```bash
# CLI 실행
python main.py samples/1706.03762v7.pdf --max-workers 8

# 웹 UI에서 동일 파일 번역 (workers=8)
# 결과물 비교: 동일한 파일이 생성되어야 함
```

---

## 예상 효과

- **웹 UI 번역 속도**: 현재 대비 4.7배 향상 (CLI와 동일)
- **사용자 경험**: 워커 수 조절로 시스템 리소스에 맞게 최적화 가능
- **일관성**: CLI와 웹 UI가 동일한 성능 제공

---

## 주의사항

1. **API Rate Limiting**: 워커 수가 너무 높으면 번역 API가 429 에러를 반환할 수 있음
   - 슬라이더 최대값을 16으로 제한
   - Help 텍스트로 권장값(8) 명시

2. **메모리 사용**: 대용량 PDF + 높은 워커 수는 메모리를 많이 사용
   - 현재는 경고만 표시, 향후 메모리 모니터링 추가 고려

3. **에러 처리**: `process_document` 호출 시 기존 try-except 블록 유지

---

*계획 작성 완료: 2025-11-22*

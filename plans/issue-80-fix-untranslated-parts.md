# Issue #80: 영어 번역 안 된 부분 수정

## 목표

웹 뷰어(`app.py`)에서 문서 처리 진행 상황 메시지가 언어 설정에 맞게 표시되도록 하고, 언어 변경 시 업로드된 파일이 초기화되는 문제를 해결합니다. 또한, 영문 문서(`docs/README.en.md`)의 누락된 내용을 보완합니다.

## 배경

- **진행 메시지 미번역**: `src/core.py` 내부에 진행 상태 메시지("문서 구조 분석 및 변환 중...")가 한국어로 하드코딩되어 있어, 영어 설정에서도 한국어로 표시됩니다.
- **언어 변경 시 초기화**: `app.py`에서 언어 변경 시 `st.file_uploader`의 라벨(`label`)이 바뀌면서 컴포넌트가 재생성되어 업로드된 파일이 사라지는 문제가 있습니다.
- **영문 문서 누락**: `docs/README.en.md`에 `SUPPORT.md` 링크 등 일부 내용이 누락되어 있습니다.

## 제안 변경 사항

### src/core.py

#### [MODIFY] [core.py](file:///c:/github/docling-translate/src/core.py)

**변경 내용**:
- `PROGRESS_MESSAGES` 딕셔너리 상수를 추가하여 한국어/영어 진행 메시지를 관리합니다.
- `process_single_file` 및 `process_document` 함수에 `ui_lang` 파라미터(기본값 "ko")를 추가합니다.
- 하드코딩된 메시지 대신 `ui_lang`에 따른 메시지를 `progress_cb`로 전달합니다.

**핵심 코드**:
```python
PROGRESS_MESSAGES = {
    "ko": {
        "analyzing": "📄 문서 구조 분석 및 변환 중... ({file_name})",
        "error_not_found": "❌ 오류: 파일을 찾을 수 없음 ({file_name})",
        # ...
    },
    "en": {
        "analyzing": "📄 Analyzing document structure... ({file_name})",
        "error_not_found": "❌ Error: File not found ({file_name})",
        # ...
    }
}

def process_single_file(..., ui_lang: str = "ko"):
    msgs = PROGRESS_MESSAGES.get(ui_lang, PROGRESS_MESSAGES["ko"])
    # ...
    if progress_cb:
        progress_cb(0.02, msgs["analyzing"].format(file_name=file_name))
```

### app.py

#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)

**변경 내용**:
- `process_document` 호출 시 `ui_lang=get_current_lang()`을 전달합니다.
- `st.file_uploader`의 초기화 문제를 해결하기 위해:
    - `label_visibility="collapsed"`로 설정하여 라벨 변경으로 인한 재생성을 방지합니다.
    - 대신 `st.markdown`을 사용하여 동적으로 라벨을 표시합니다.
    - `key="file_uploader"`를 명시하여 컴포넌트의 Identity를 유지합니다.

**핵심 코드**:
```python
    # 라벨 직접 렌더링
    st.markdown(f"<label class='stWidgetLabel'>{t('upload_label')}</label>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        label="file_uploader", # 고정 라벨 (화면엔 안 보임)
        label_visibility="collapsed",
        key="file_uploader", # 고정 Key
        # ...
    )

    # ...
    process_document(..., ui_lang=get_current_lang())
```

### 문서 (Docs)

#### [MODIFY] [README.en.md](file:///c:/github/docling-translate/docs/README.en.md)

**변경 내용**:
- `README.md`와 내용을 동기화합니다.
- **누락된 부분 추가**:
    - **CLI Usage**: LFM2 모델 실행 예시 추가.
    - **Installation**: 로컬 모델 설치 설명에서 Qwen 외 LFM2, Yanolja 언급 추가.
    - **Support**: `SUPPORT.md` 링크 섹션 추가.

### 참고: CLI (main.py)
- **변경 없음**: 사용자 요청에 따라 CLI는 수정하지 않습니다. 

---

## 검증 계획

### 1. 자동 테스트
- 기존 테스트 코드가 없으므로 수동 테스트에 의존합니다.

### 2. 수동 테스트

**시나리오 1: 웹 뷰어 언어 변경 및 파일 유지 확인**
- 단계:
  1. `streamlit run app.py` 실행
  2. PDF 파일 1개 업로드
  3. 사이드바에서 언어를 "English"로 변경
- 예상 결과:
  1. 페이지가 새로고침되어도 업로드된 파일이 **유지**되어야 함.
  2. "Upload documents..." 라벨이 영어로 정상 표시되어야 함.

**시나리오 2: 웹 뷰어 진행 메시지 번역 확인**
- 단계:
  1. 언어를 "English"로 설정
  2. PDF 번역 시작
- 예상 결과:
  1. 진행 바 밑의 텍스트가 "📄 Analyzing document structure..." 등 **영어**로 표시되어야 함. (기존 한국어 메시지 안 나와야 함)

### 3. 검증 체크리스트

- [ ] `app.py`에서 언어 변경 시 파일 유지됨
- [ ] `app.py` 번역 진행 시 영어 메시지 출력됨 (영어 설정 시)
- [ ] `README.en.md` 내용이 `README.md`와 동기화됨 (LFM2 예시 등 포함)

---

## 주의사항

- `st.file_uploader`의 `label_visibility="collapsed"`를 사용할 때 접근성(Accessibility) 문제가 없는지 확인 (커스텀 라벨 추가로 해결).
- `src/core.py`는 순수 Python 모듈이어야 하므로 `streamlit` 의존성을 추가하지 않도록 주의.

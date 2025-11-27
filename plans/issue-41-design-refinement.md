# Issue #41: 디자인 다듬기 (Design Refinement)

## 목표

사용자 피드백을 반영하여 UI 요소의 위치를 조정하고, 번역되지 않은 기본 텍스트를 처리합니다.

## 배경

1.  **언어 전환 버튼 위치**: 현재 좌측 상단(`[1, 5]` 비율)에 위치하여 다소 어색합니다. 이를 **우측 상단**(`[5, 1]` 비율)으로 이동하여 일반적인 웹사이트의 네비게이션 바와 유사한 느낌을 주도록 개선합니다.
2.  **파일 업로더 텍스트**: Streamlit의 `file_uploader` 위젯 내부 텍스트("Drag and drop files here", "Limit 200MB...")는 기본적으로 번역 API를 제공하지 않습니다. CSS Hack을 통해 이를 한국어/영어로 동적으로 변경하는 시도를 합니다.

## 제안 변경 사항

### 1. `app.py` (버튼 위치 이동)

#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)

**변경 내용**:
*   컬럼 구성을 `st.columns([1, 5])`에서 `st.columns([5, 1])` (또는 적절한 비율)로 변경하여 버튼을 오른쪽으로 보냅니다.
*   타이틀이 먼저 오고, 버튼이 나중에 오도록 순서를 바꿉니다.
*   버튼의 수직 정렬을 맞추기 위해 CSS나 빈 공간(`st.write("")`)을 활용할 수 있습니다.

### 2. `app.py` (CSS Hack for Uploader)

#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)

**변경 내용**:
*   `st.markdown`을 사용하여 CSS를 주입합니다.
*   `[data-testid="stFileUploaderDropzoneInstructions"]` 등의 선택자를 사용하여 내부 텍스트를 숨기고(`visibility: hidden`), `::after` 가상 요소를 사용하여 새로운 텍스트를 넣습니다.
*   현재 언어(`st.session_state["lang"]`)에 따라 CSS 내용을 동적으로 생성합니다.

**핵심 코드 (CSS Hack)**:

```python
# i18n 딕셔너리에 업로더 텍스트 추가
TRANSLATIONS = {
    "en": { ..., "uploader_text": "Drag and drop files here", "uploader_limit": "Limit 200MB per file..." },
    "ko": { ..., "uploader_text": "파일을 이곳에 드래그 앤 드롭하세요", "uploader_limit": "파일당 200MB 제한..." }
}

# main() 함수 내
uploader_css = f"""
<style>
[data-testid="stFileUploaderDropzoneInstructions"] > div:first-child {{
    visibility: hidden;
}}
[data-testid="stFileUploaderDropzoneInstructions"] > div:first-child::after {{
    content: "{t('uploader_text')}";
    visibility: visible;
    display: block;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
}}
/* Limit 텍스트 처리도 유사하게... (복잡할 수 있음) */
</style>
"""
st.markdown(uploader_css, unsafe_allow_html=True)
```

**주의**: Streamlit 버전 업데이트에 따라 클래스명이나 구조가 바뀌면 깨질 수 있는 방식입니다. 하지만 현재로서는 유일한 방법입니다. "Limit..." 부분은 구조가 복잡하여 완벽하게 바꾸기 어려울 수 있으므로, 메인 텍스트("Drag and drop...") 위주로 변경을 시도합니다.

---

## 검증 계획

### 1. 수동 테스트

**시나리오 1: 버튼 위치 확인**
- 앱 실행 시 "English/한국어" 버튼이 우측 상단에 위치하는지 확인.

**시나리오 2: 업로더 텍스트 확인**
- 언어 전환 시 파일 업로드 영역의 "Drag and drop..." 텍스트가 한국어/영어로 바뀌는지 확인.

---

## 예상 효과

- **심미성**: 버튼 위치가 자연스러워짐.
- **완성도**: 영문으로 남아있던 부분이 번역되어 앱의 완성도가 높아짐.

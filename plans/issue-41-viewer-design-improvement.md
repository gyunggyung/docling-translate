# Issue #41: 뷰어 디자인 향상 (Viewer Design Improvement)

## 목표

Streamlit 웹 앱(`app.py`)의 언어 선택 UI를 개선하고, 생성되는 결과물 HTML(`main.py`)에 다크 모드와 다국어 UI를 적용하여 전체적인 사용자 경험을 향상시킵니다.

## 배경

1.  **`app.py` UI**: 현재 언어 선택 기능이 라디오 버튼으로 구현되어 있어 디자인이 투박하고 공간을 많이 차지합니다. 이를 클릭 한 번으로 언어가 전환되는 직관적인 버튼 형태로 개선해야 합니다.
2.  **HTML 결과물**: 생성되는 인터랙티브 HTML 파일이 브라우저 다크 모드를 지원하지 않으며, 뷰어 자체의 UI(버튼 등)가 영어로 고정되어 있어 한국어 사용자에게 불편함을 줍니다.

## 제안 변경 사항

### 1. `app.py` (웹 앱 UI 개선)

#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)

**변경 내용**:
*   기존의 `st.radio` 기반 언어 선택기를 제거합니다.
*   대신 `st.button`을 사용하여 클릭 시 언어가 토글(Korean ↔ English)되도록 변경합니다.
*   버튼의 텍스트는 현재 언어의 반대 언어(전환될 언어)를 표시하여 직관성을 높입니다.
    *   현재 한국어인 경우: "English" 버튼 표시
    *   현재 영어인 경우: "한국어" 버튼 표시
*   레이아웃을 조정하여 타이틀과 자연스럽게 어우러지도록 합니다.

**핵심 코드 예시**:

```python
# 변경 전
# selected_label = st.radio(...)

# 변경 후
with col_lang:
    current_lang = get_current_lang()
    # 현재가 한국어면 'English' 버튼, 영어면 '한국어' 버튼 표시
    next_lang = "en" if current_lang == "ko" else "ko"
    btn_label = "English" if current_lang == "ko" else "한국어"
    
    if st.button(btn_label, key="lang_toggle"):
        set_current_lang(next_lang)
        st.rerun()
```

---

### 2. `main.py` (HTML 템플릿 디자인 개선)

#### [MODIFY] [main.py](file:///c:/github/docling-translate/main.py)

**변경 내용**:
*   **CSS 변수 기반 테마 시스템**: 라이트/다크 모드 색상 변수를 정의하고, `data-theme` 속성으로 제어합니다.
*   **HTML 뷰어 i18n**: 뷰어 내의 버튼(다크 모드 전환, 뷰 모드 전환 등) 텍스트를 한국어/영어로 전환할 수 있는 JavaScript 기능을 추가합니다.
*   **컨트롤 바 디자인**: 단순 버튼 나열 대신, 아이콘이나 깔끔한 메뉴 형태로 컨트롤 바를 개선합니다.

**핵심 코드 (HTML_HEADER 수정)**:

```html
<script>
    // 뷰어 내부 UI 번역
    const UI_STRINGS = {
        en: { theme: "Dark Mode", layout: "Inline View", lang: "Show Korean" },
        ko: { theme: "다크 모드", layout: "한줄 보기", lang: "원문 보기" }
    };
    // ... 토글 로직 ...
</script>
```

---

## 검증 계획

### 1. 수동 테스트

**시나리오 1: 앱 언어 전환 (`app.py`)**
- 단계:
  1. `streamlit run app.py` 실행.
  2. 좌측 상단의 "English" (또는 "한국어") 버튼 클릭.
- 예상 결과:
  - 페이지가 새로고침되며 UI 텍스트가 해당 언어로 변경되어야 함.
  - 버튼 텍스트가 반대 언어로 변경되어야 함.

**시나리오 2: HTML 뷰어 기능 (`main.py`)**
- 단계:
  1. 문서를 변환하여 결과 HTML을 생성 및 오픈.
  2. 뷰어 상단의 "다크 모드" 버튼 클릭.
  3. 뷰어 상단의 언어 전환 버튼 클릭.
- 예상 결과:
  - 배경색이 어둡게 변하고 텍스트 색상이 밝게 변해야 함.
  - 뷰어의 버튼 텍스트들이 한국어 ↔ 영어로 전환되어야 함.

### 2. 검증 체크리스트

- [ ] `app.py`의 라디오 버튼이 사라지고 토글 버튼으로 대체되었는가?
- [ ] `app.py` 언어 전환 시 상태가 유지되는가?
- [ ] 생성된 HTML 파일이 다크 모드를 지원하는가?

---

## 예상 효과

- **심미성**: 웹 앱의 상단 디자인이 훨씬 깔끔하고 모던해집니다.
- **편의성**: 사용자가 원하는 언어와 테마 환경에서 문서를 열람할 수 있습니다.

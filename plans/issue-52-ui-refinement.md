# Issue #52 Follow-up: UI 레이아웃 개선

## 목표

사용자 요청에 따라 "집중 모드" 토글을 제거하고, 항상 집중 모드(단일 컬럼) 레이아웃을 기본값으로 적용합니다. 또한 "폴더 열기" 버튼을 번역 결과 하단에 배치하여 UI를 단순화합니다.

## 배경

현재 UI는 "집중 모드" 토글을 통해 1컬럼(집중)과 2컬럼(기본) 레이아웃을 전환할 수 있습니다. 사용자는 집중 모드를 기본값으로 하고 토글을 제거하여 더 직관적이고 단순한 UI를 원합니다.

## 제안 변경 사항

### UI (Streamlit)

#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)

**변경 내용**:
- **집중 모드 토글 제거**: `st.toggle("focus_mode_label", ...)` 코드 제거.
- **검수 모드 토글 제거**: `st.toggle("view_mode_label", ...)` 코드 제거.
- **기본값 설정**: 검수 모드(Inspection Mode)는 기본적으로 활성화 상태로 스크립트 주입.
- **레이아웃 통합**: `if focus_mode:` 분기 제거 및 항상 1컬럼 레이아웃 적용.
- **폴더 열기 버튼 배치**: 번역 결과 뷰어 하단에 "폴더 열기" 버튼 배치.

**변경 전**:
```python
c_head, c_blank, c_view, c_focus = st.columns([6, 2, 2, 2])
with c_view:
    view_mode = st.toggle(...)
with c_focus:
    focus_mode = st.toggle(...)

if focus_mode:
    # ...
```

**변경 후**:
```python
# 토글 제거 및 항상 1컬럼 레이아웃
# view_mode는 True로 고정 (스크립트 주입)

st.info(t("single_tip"))
st.components.v1.html(html_content, height=900, scrolling=True)
```

## 검증 계획

### 수동 테스트

**시나리오 1: UI 레이아웃 확인**
- 단계:
  1. `streamlit run app.py` 실행.
  2. PDF 파일 업로드 및 번역 실행.
  3. 결과 화면에서 "집중 모드" 토글이 사라졌는지 확인.
  4. 번역 결과가 화면 전체 너비(1컬럼)로 표시되는지 확인.
  5. 뷰어 하단에 "폴더 열기" 버튼이 위치하고 정상 작동하는지 확인.

# Issue #23: 웹 뷰어 인터페이스 개선 계획 (수정됨)

## 목표 설명 (Goal Description)
초기 구현된 Streamlit 웹 뷰어의 부족한 점(이미지/표 미지원, HTML 뷰 부재, 다운로드 오류, 히스토리 미지원)을 보완하여 완성도 높은 인터페이스를 제공합니다.

## 사용자 검토 필요 (User Review Required)
> [!IMPORTANT]
> **구조 변경**: `main.py`의 `process_document` 함수가 단순히 파일을 쓰는 것을 넘어, `app.py`에서 결과를 활용할 수 있도록 리팩토링합니다.
> **HTML 뷰**: Streamlit 내에서 `st.components.v1.html`을 사용하여 `main.py`가 생성한 인터랙티브 HTML을 직접 렌더링합니다.

## 변경 제안 (Proposed Changes)

### 1. 핵심 로직 리팩토링
#### [MODIFY] [main.py](file:///c:/github/docling-translate/main.py)
- `process_document` 함수가 생성된 파일들의 경로와 메타데이터를 반환하도록 수정합니다.
- 이미지 저장 로직이 `app.py`에서도 동일하게 동작하도록 경로 처리 방식을 통일합니다.

### 2. 웹 뷰어 기능 개선
#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)
- **히스토리 기능**: `output/` 디렉토리를 스캔하여 이전에 번역된 문서 목록을 사이드바에 표시하고, 선택 시 해당 결과를 다시 로드합니다.
- **이미지/표 지원**: `main.py`를 통해 생성된 마크다운/HTML을 그대로 활용하여 이미지와 표가 깨지지 않고 표시되도록 합니다.
- **인터랙티브 뷰**: "전체 텍스트" 탭 대신 "인터랙티브 뷰" 탭을 만들고, 생성된 HTML 파일(`_interactive.html`)을 iframe 형태로 임베딩하여 원문 클릭 시 번역문이 나오는 기능을 제공합니다.
- **다운로드 개선**:
    - 개별 파일(Markdown, HTML) 다운로드 버튼 제공.
    - 전체 결과(이미지 포함)를 ZIP으로 압축하여 다운로드하는 기능 추가.

## 검증 계획 (Verification Plan)

### 수동 검증 (Manual Verification)
1. **히스토리 확인**: 앱 실행 시 기존 `output/` 폴더의 번역 결과들이 사이드바에 뜨는지 확인.
2. **신규 번역 & 이미지**: `samples/1706.03762v7.pdf` (이미지/표 포함)를 업로드하여 번역.
    - 결과 화면에서 이미지가 정상적으로 보이는지 확인.
3. **HTML 동작**: "인터랙티브 뷰" 탭에서 문장을 클릭했을 때 원문/번역문 토글이 잘 되는지 확인.
4. **다운로드**: ZIP 다운로드 후 압축을 풀었을 때 이미지와 마크다운이 정상적으로 연결되어 있는지 확인.

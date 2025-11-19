# Issue #16: HTML 형식 저장 (인터랙티브 뷰어)

## 목표
- 번역 결과를 HTML 파일로 저장하는 기능을 추가합니다.
- **기본적으로 번역문**을 보여주며, 사용자가 문장을 **클릭하면 바로 아래에 원문이 펼쳐지는(Expand)** 인터랙티브 기능을 구현합니다.
    - 이를 통해 번역문과 원문을 동시에 비교할 수 있게 합니다.
- 기존 3개 파일(원문 MD, 번역 MD, 결합 MD)에 더해 HTML 파일까지 **총 4개 파일을 기본적으로 생성**합니다.

## 구현 단계 (Task Breakdown)

### 1. HTML 생성 로직 구현
- [ ] `main.py` 내에 HTML 생성을 위한 템플릿(CSS, JS 포함) 정의
    - **CSS:**
        - 번역문: 클릭 가능하다는 것을 알 수 있도록 커서 및 스타일 지정.
        - 원문: 번역문 바로 아래에 위치하며, 초기에는 숨김(`display: none`) 처리. 구분을 위해 배경색이나 폰트 스타일 차별화.
    - **JS:** 클릭 이벤트 핸들러 (원문 영역 표시/숨김 토글).
- [ ] 문장 단위 구조:
    ```html
    <div class="sentence-container">
        <div class="translated" onclick="toggleOriginal(this)">번역된 문장...</div>
        <div class="original" style="display: none;">Original sentence...</div>
    </div>
    ```

### 2. `process_document` 함수 수정
- [ ] 기존 Markdown 출력 로직 유지.
- [ ] `translate_by_sentence` 루프 내에서 HTML 문자열도 함께 조립.
- [ ] `_interactive.html` 파일 저장 로직 추가 (별도 옵션 없이 기본 수행).

### 3. 리소스 처리
- [ ] 이미지/테이블: HTML 내에서도 `<img>` 태그로 정상적으로 보이도록 상대 경로 설정.

## 변경 파일 목록
- [MODIFY] `main.py`: HTML 생성 및 파일 쓰기 로직 추가.

## 검증 계획
- [ ] 생성된 HTML 파일을 열어 번역문 클릭 시 아래에 원문이 나오는지 확인.
- [ ] 원문이 나온 상태에서 번역문과 원문을 동시에 볼 수 있는지 확인.
- [ ] 총 4개의 파일이 생성되는지 확인.


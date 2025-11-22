# Issue #26: 뷰어 UI/UX 향상 - 듀얼 뷰 모드 구현

## 목표
웹 뷰어와 생성되는 HTML 파일의 UI/UX를 개선하여, 사용자가 자신의 선호에 따라 **"좌우 병렬 보기(Side-by-Side)"**와 **"클릭하여 펼치기(Expand/Collapse)"** 두 가지 방식을 자유롭게 전환하며 읽을 수 있도록 합니다.

## 배경
- 기존 "클릭하여 원문 보기" 방식은 모바일이나 좁은 화면에서 유용하지만, PC에서는 비교가 번거로움.
- 전문 번역 작업에는 "좌우 병렬 보기"가 표준이지만, 가벼운 독서에는 "펼치기"가 나을 수 있음.
- 두 가지 장점을 모두 수용하기 위해 **하나의 HTML 파일 내에서 뷰 모드를 토글**할 수 있는 기능을 구현하고자 함.

## 제안 변경 사항

### 1. `main.py`: HTML 템플릿 및 생성 로직 전면 수정

#### [MODIFY] [main.py](file:///c:/github/docling-translate/main.py)

**변경 내용**:
- **HTML 헤더에 컨트롤 패널 추가**: 상단에 "View Mode: Side-by-Side / Inline" 토글 버튼 배치.
- **CSS 개선**:
    - 기본적으로 `Side-by-Side` 모드를 활성화 (`.view-mode-side`).
    - 클래스 변경 시 `Inline(Expand)` 모드로 전환 (`.view-mode-inline`).
- **JS 로직 추가**: 버튼 클릭 시 최상위 컨테이너의 클래스를 교체하여 CSS 모드 전환.

**핵심 코드 구조 (HTML/CSS/JS)**:

```python
HTML_HEADER = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Docling Translation Result</title>
    <style>
        :root { --bg-color: #f4f6f8; --card-bg: #fff; --border: #eee; --hover: #eef7ff; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg-color); margin: 0; padding: 20px; }
        .controls { text-align: right; margin-bottom: 15px; position: sticky; top: 10px; z-index: 100; }
        .btn-toggle { padding: 8px 16px; background: #333; color: #fff; border: none; border-radius: 20px; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        .container { max-width: 1200px; margin: 0 auto; background: var(--card-bg); box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-radius: 8px; overflow: hidden; }
        
        /* 공통 스타일 */
        .row { border-bottom: 1px solid var(--border); transition: background 0.2s; }
        .row:hover { background-color: var(--hover); }
        .src, .tgt { padding: 14px 20px; line-height: 1.6; }
        .src { color: #666; font-size: 0.95em; background-color: #fafafa; }
        .tgt { color: #222; font-weight: 500; }
        
        /* 1. Side-by-Side Mode (Default) */
        .view-mode-side .row { display: grid; grid-template-columns: 1fr 1fr; }
        .view-mode-side .src { border-right: 1px solid var(--border); }
        
        /* 2. Inline (Expand) Mode */
        .view-mode-inline .row { display: block; }
        .view-mode-inline .src { display: none; border-left: 4px solid #ccc; margin: 0 20px 10px; border-right: none; background: #f1f1f1; border-radius: 4px; }
        .view-mode-inline .tgt { cursor: pointer; }
        .view-mode-inline .tgt::after { content: ' ▾'; color: #999; font-size: 0.8em; }
        .view-mode-inline .row.active .src { display: block; } /* JS로 active 토글 */

        /* 이미지/표 공통 */
        .full-width { grid-column: 1 / -1; padding: 20px; text-align: center; border-bottom: 1px solid var(--border); }
        img { max-width: 100%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }

        /* 모바일 반응형 (강제 Inline) */
        @media (max-width: 768px) {
            .view-mode-side .row { grid-template-columns: 1fr; }
            .view-mode-side .src { border-right: none; border-bottom: 1px dashed #ddd; }
        }
    </style>
    <script>
        function toggleMode() {
            const container = document.getElementById('content-container');
            const btn = document.getElementById('mode-btn');
            if (container.classList.contains('view-mode-side')) {
                container.classList.remove('view-mode-side');
                container.classList.add('view-mode-inline');
                btn.innerText = 'Switch to Side-by-Side View';
            } else {
                container.classList.remove('view-mode-inline');
                container.classList.add('view-mode-side');
                btn.innerText = 'Switch to Inline View';
            }
        }
        
        function toggleInline(el) {
            // Inline 모드일 때만 동작
            const container = document.getElementById('content-container');
            if (container.classList.contains('view-mode-inline')) {
                el.parentElement.classList.toggle('active');
            }
        }
    </script>
</head>
<body>
    <div class="controls">
        <button id="mode-btn" class="btn-toggle" onclick="toggleMode()">Switch to Inline View</button>
    </div>
    <h1>Translation Result</h1>
    <div id="content-container" class="container view-mode-side">
"""
```

### 2. `app.py`: 뷰어 안내 개선

#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)
- 인터랙티브 뷰 탭에 안내 문구 추가: "우측 상단의 버튼을 눌러 뷰 모드(좌우 병렬 / 펼치기)를 변경할 수 있습니다."

---

## 검증 계획

### 1. HTML 기능 테스트
- 생성된 HTML 파일을 브라우저에서 열고:
    1.  **Side-by-Side (기본)**: 좌우로 잘 나오는지 확인.
    2.  **버튼 클릭**: "Inline View"로 레이아웃이 즉시 바뀌는지 확인.
    3.  **Inline 모드**: 번역문 클릭 시 원문이 아래에 펼쳐지는지 확인.
    4.  **다시 버튼 클릭**: Side-by-Side로 돌아오는지 확인.

### 2. 웹 뷰어 통합 테스트
- `streamlit run app.py` 실행.
- iframe 내부에서도 토글 버튼이 정상 동작하는지 확인.

---

## 예상 효과
- **사용자 선택권 보장**: 집중해서 비교하고 싶을 땐 Side-by-Side, 가볍게 읽을 땐 Inline 모드 선택 가능.
- **완성도 향상**: 단순한 텍스트 나열이 아닌, 기능적인 웹 애플리케이션 형태의 결과물 제공.

---

## 주의사항
- 모바일 화면에서는 Side-by-Side가 오히려 불편할 수 있으므로, 미디어 쿼리(`@media`)로 좁은 화면에서는 자동으로 상하 배치되도록 CSS 처리(이미 포함됨).

*계획 작성일: 2025-11-22*

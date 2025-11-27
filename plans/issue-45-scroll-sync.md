# Issue #45: 모드 전환 시 스크롤 위치 동기화

## 목표

읽기 모드와 검수 모드 간 전환 시, 사용자가 보고 있던 문장의 위치가 유지되도록 스크롤 위치를 동기화합니다.

## 배경

현재 모드 전환 시 레이아웃이 크게 변경(단일 컬럼 <-> 2단 컬럼)되면서 전체 문서의 높이가 달라져, 사용자가 보고 있던 위치를 놓치는 문제가 발생합니다.

## 제안 변경 사항

### `main.py` (HTML 템플릿 JS 수정)

#### [MODIFY] [main.py](file:///c:/github/docling-translate/main.py)

**변경 내용**:

1.  **`toggleMode()` 함수 개선**:
    *   모드 전환 **전**, 현재 뷰포트(화면) 최상단에 위치한 가장 가까운 문장 요소(`span.sent`)를 찾습니다.
    *   모드 전환 **후**, 해당 문장 요소가 다시 화면 상단에 오도록 `scrollIntoView()` 또는 `scrollTo()`를 호출합니다.

**핵심 로직 (JavaScript)**:
```javascript
function toggleMode() {
    // 1. 현재 보이는 첫 번째 문장 찾기
    const sents = document.querySelectorAll('.sent');
    let targetSent = null;
    for (let sent of sents) {
        const rect = sent.getBoundingClientRect();
        if (rect.top >= 0 && rect.top < window.innerHeight) {
            targetSent = sent;
            break;
        }
    }

    // 2. 모드 전환
    const container = document.getElementById('content-container');
    const btn = document.getElementById('btn-mode');
    // ... (기존 토글 로직) ...

    // 3. 위치 복원
    if (targetSent) {
        targetSent.scrollIntoView({ behavior: 'auto', block: 'center' });
    }
}
```

## 검증 계획

### 1. 수동 테스트
- 단계:
  1. 긴 문서를 변환하여 HTML을 엽니다.
  2. 문서 중간으로 스크롤합니다.
  3. '검수 모드' 버튼을 클릭합니다.
  4. 화면이 엉뚱한 곳으로 튀지 않고, 방금 보고 있던 문장이 화면 내에 유지되는지 확인합니다.
  5. 다시 '읽기 모드'로 전환하여 동일하게 확인합니다.

---

*계획 작성일: 2025-11-27*

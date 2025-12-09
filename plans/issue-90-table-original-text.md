# Issue #90: 표 번역 원문 표시 기능 추가

## 목표

표(Table) 번역 시, 번역된 텍스트뿐만 아니라 원문 텍스트도 함께 표시하여 사용자가 번역의 정확성을 검증할 수 있도록 합니다.

## 배경

현재는 표를 이미지로 표시하고, 추가로 번역된 표(텍스트)를 `details` 태그로 제공하고 있습니다. 하지만 표 내부 텍스트의 번역이 부정확한 경우(고유명사, 수치 등), 원문과 비교하기가 어렵습니다. 일반 텍스트 문단처럼 표도 원문 텍스트를 확인할 수 있는 기능이 필요합니다.

## 제안 변경 사항

### HTML 렌더링 로직 개선

#### [MODIFY] [src/html_generator.py](file:///c:/github/docling-translate/src/html_generator.py)

**변경 내용**:
- `generate_html_content` 함수 내 `TableItem` 처리 로직을 수정합니다.
- **Reading Mode**: 기존처럼 번역문 표만 보이며, 마우스 오버 시 원문 툴팁 제공.
- **Inspection Mode**: `.src-block`과 `.tgt-block` 구조를 활용하여 **좌측: 원문 표, 우측: 번역 표**가 나란히 표시되도록 함.

**핵심 코드**:
```python
# [NEW] 원문 표 생성 (툴팁 없음, 순수 원문)
df = item.export_to_dataframe()
# ... (원문 그대로 HTML 변환) ...
table_html_orig = ...

# [NEW] 번역 표 생성 (툴팁 포함)
# ... (기존 로직) ...
table_html_trans = ...

# HTML 구조 변경
# paragraph-row 안에 src-block / tgt-block을 배치하여 
# 검수 모드 CSS(grid-template-columns: 1fr 1fr)가 자연스럽게 적용되도록 함.
html_parts.append(f"""
<div class="full-width">
    <details>
        <summary ...>📋 번역된 표 보기 (텍스트)</summary>
        <div class="paragraph-row">
            <!-- 원문 표 (검수 모드에서만 보임) -->
            <div class="src-block">
                <div class="table-container">
                    {table_html_orig}
                </div>
            </div>
            <!-- 번역 표 (항상 보임) -->
            <div class="tgt-block">
                <div class="table-container">
                    {table_html_trans}
                </div>
            </div>
        </div>
    </details>
</div>
""")
```
- 별도의 CSS 추가 없이 기존 `.view-mode-inspect .paragraph-row` 스타일을 그대로 활용할 수 있어 효율적입니다.

---

## 검증 계획

### 수동 테스트
1. **변환 실행**: `python main.py samples/1706.03762v7.pdf`
2. **UI 확인**:
   - **읽기 모드**: 표 하나만 보임 (번역본). 마우스 오버 시 툴팁 작동.
   - **검수 모드**: 표 두 개가 나란히 보임 (좌: 원문, 우: 번역본).
   - `Details` 태그가 이 레이아웃을 잘 감싸는지 확인.

---

## 검증 계획

### 수동 테스트
1. **변환 실행**: `python main.py samples/1706.03762v7.pdf`
2. **UI 확인**:
   - '번역된 표 보기'를 펼침.
   - 표 안의 한글 텍스트에 마우스를 올렸을 때, **영어 원문이 툴팁으로 뜨는지** 확인.
   - 툴팁 위치가 적절한지 확인.

---

## 예상 효과

- 사용자는 부정확한 표 번역을 원문과 즉시 대조하여 검증할 수 있습니다.
- 표 데이터의 신뢰도가 향상됩니다.

*계획 작성일: 2025-12-09*

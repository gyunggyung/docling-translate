# Issue #36: 코드 정리

## 목표

프로젝트의 유지보수성과 가독성을 높이기 위해 불필요한 코드, 파일, 기능을 제거하고, 코드 구조를 개선하여 프로젝트를 깔끔하게 정리합니다.

## 배경

프로젝트가 여러 기능 개선을 거치면서 코드가 점점 복잡해지고, 이제는 사용하지 않는 파일과 기능들이 남아있습니다. 또한 README와 문서들이 최신 기능을 반영하지 못하고 있습니다. 이번 정리 작업을 통해 프로젝트를 더 보기 좋고 이해하기 쉽게 만들고자 합니다.

관련 이슈: [#36](https://github.com/gyunggyung/docling-translate/issues/36)

## 제안 변경 사항

### 1. 불필요한 파일 제거

#### [DELETE] [`.gitattributes`](file:///c:/github/docling-translate/.gitattributes)

**이유**: 
- 단순히 `* text=auto eol=lf`만 포함하고 있으며, Git의 기본 설정으로 충분
- 프로젝트에 특별한 라인 엔딩 관리가 필요하지 않음

---

#### [DELETE] [`CHANGELOG.md`](file:///c:/github/docling-translate/CHANGELOG.md)

**이유**:
- GitHub Releases와 중복되는 정보
- 유지보수 부담만 증가시킴
- GitHub의 Release Notes와 Issues로 변경 이력 추적 가능

---

#### [DELETE] 디버그 파일들

**삭제할 파일**:
- `debug_log_2.txt`
- `debug_output.txt`
- `test_parallel.py` (임시 테스트 파일)

**이유**: 
- 디버깅용 임시 파일로 더 이상 필요 없음
- `.gitignore`에 `debug_*.txt` 패턴 추가하여 향후 유사 파일 방지

---

### 2. Markdown 파일 저장 기능 제거

#### [MODIFY] [`main.py`](file:///c:/github/docling-translate/main.py)

**변경 내용**:
- Markdown 파일 생성 코드 제거 (`*_en.md`, `*_ko.md`, `*_combined.md`)
- HTML 파일만 생성하도록 단순화
- 이미지 저장 기능은 유지 (HTML에서 필요)

**근거**:
- HTML 뷰어만으로 충분히 원문/번역문 확인 가능
- 사용자들이 Markdown을 직접 사용하는 경우가 거의 없음
- 파일 생성 오버헤드 감소 및 코드 단순화

**예상 코드 변경**:
```python
# 변경 전: 3개의 MD 파일 + 1개의 HTML 파일 생성
with open(path_src, "w") as f_src, \
     open(path_target, "w") as f_target, \
     open(path_combined, "w") as f_comb, \
     open(path_html, "w") as f_html:
    # ...

# 변경 후: HTML 파일만 생성
with open(path_html, "w", encoding="utf-8") as f_html:
    # ...
```

---

#### [MODIFY] [`app.py`](file:///c:/github/docling-translate/app.py)

**변경 내용**:
- Markdown 관련 다운로드/표시 기능 제거
- HTML 뷰어와 ZIP 다운로드만 유지
- 인터페이스 단순화

---

### 3. 코드 주석 개선

#### [MODIFY] [`main.py`](file:///c:/github/docling-translate/main.py)

**변경 내용**:
- 과도하게 상세한 주석 정리 (1-4번 줄의 기본 import 설명 등)
- 핵심 로직에만 명확한 한글 주석 추가
- 함수 시그니처에 Type Hint와 docstring으로 설명 강화

**예시**:
```python
# 변경 전
# argparse: 커맨드 라인 인자를 파싱하기 위해 사용합니다.
# os: 운영 체제와 상호 작용하기 위해 사용합니다. (예: 경로 확인)
# pathlib.Path: 파일 시스템 경로를 객체 지향적으로 다루기 위해 사용합니다.
# logging: 프로그램 실행 중 정보를 기록하기 위해 사용합니다.
import argparse
import os
from pathlib import Path
import logging

# 변경 후
import argparse
import os
from pathlib import Path
import logging
```

---

#### [MODIFY] [`translator.py`](file:///c:/github/docling-translate/translator.py)

**변경 내용**:
- 각 엔진별 번역 함수의 docstring 보강
- 재시도 로직에 대한 명확한 주석 추가
- 불필요한 주석 제거

---

### 4. 코드 구조 개선 (모듈화)

#### [NEW] [`src/`](file:///c:/github/docling-translate/src/) 폴더 구조

**목적**: 코드를 기능별로 분리하여 가독성과 유지보수성 향상

**제안 구조**:
```
src/
├── __init__.py
├── converter.py      # Docling 변환 로직
├── translator.py     # 번역 엔진 통합 (현재 파일 이동)
├── html_generator.py # HTML 생성 관련 로직
└── utils.py          # 공통 유틸리티 함수
```

**주요 기능**:
- `converter.py`: DocumentConverter 초기화 및 문서 변환 로직
- `html_generator.py`: HTML_HEADER, HTML_FOOTER, HTML 생성 함수
- `utils.py`: 이미지 저장, 언어 코드 변환 등 공통 기능

**장점**:
- `main.py`가 800+ 줄에서 200줄 이하로 감소
- 각 모듈의 책임이 명확해짐
- 테스트 작성이 용이해짐

---

### 5. 문서 정리

#### [MODIFY] [`README.md`](file:///c:/github/docling-translate/README.md)

**변경 내용**:
- **기능 섹션 업데이트**: 최신 기능 반영 (검수 모드, 다양한 포맷 지원 등)
- **사용 예시 단순화**: 가장 일반적인 사용 사례만 강조
- **설치 방법 명확화**: 선택적 의존성 명시 (DeepL, Gemini, OpenAI별)
- **스크린샷 추가**: 실제 번역 결과물 예시 이미지

---

#### [MODIFY] [`docs/README.en.md`](file:///c:/github/docling-translate/docs/README.en.md)

**변경 내용**:
- `README.md`와 동기화
- 영문 사용자를 위한 명확한 설명

---

#### [MODIFY] [`docs/USAGE.md`](file:///c:/github/docling-translate/docs/USAGE.md)

**변경 내용**:
- Markdown 파일 출력 관련 내용 제거
- HTML 인터랙티브 뷰어 사용법 강화
- 검수 모드 활용 방법 추가

---

#### [MODIFY] [`docs/CONTRIBUTING.md`](file:///c:/github/docling-translate/docs/CONTRIBUTING.md)

**변경 내용**:
- 새로운 `src/` 폴더 구조 반영
- 각 모듈의 역할 명시

---

### 6. `.gitignore` 보강

#### [MODIFY] [`.gitignore`](file:///c:/github/docling-translate/.gitignore)

**추가 패턴**:
```gitignore
# 디버그 파일
debug_*.txt
debug_*.log

# 임시 테스트 파일
test_*.py
!tests/test_*.py  # tests 폴더의 테스트는 제외

# IDE 설정 (추가)
.idea/
*.swp
*.swo
```

---

## 검증 계획

### 1. 기능 테스트 (표준 샘플)

**시나리오**: 기존 기능이 정상 동작하는지 확인

```bash
# CLI 테스트
python main.py samples/1706.03762v7.pdf -f en -t ko -e google
```

**예상 결과**:
- HTML 파일이 정상적으로 생성됨
- Markdown 파일은 생성되지 않음
- 이미지와 표는 정상적으로 표시됨
- 번역 품질은 기존과 동일

### 2. 웹 UI 테스트

```bash
streamlit run app.py
```

**단계**:
1. 샘플 PDF 업로드
2. 번역 실행
3. 인터랙티브 뷰어에서 결과 확인
4. ZIP 다운로드 확인

**예상 결과**:
- UI가 더 단순하고 명확해짐
- Markdown 다운로드 버튼이 없어짐
- HTML 뷰어는 정상 동작

### 3. 모듈화 검증

**단계**:
1. `src/` 구조로 리팩토링 후 import 확인
2. 각 모듈 독립 실행 테스트
3. 전체 통합 테스트

### 4. 검증 체크리스트

- [ ] 표준 샘플(`samples/1706.03762v7.pdf`)로 CLI 테스트 성공
- [ ] 웹 UI에서 파일 업로드 및 번역 성공
- [ ] HTML 뷰어의 읽기 모드 / 검수 모드 정상 동작
- [ ] 삭제된 파일들이 더 이상 생성되지 않음 확인
- [ ] 모든 문서가 최신 기능 반영
- [ ] Git 저장소가 깔끔해짐 (불필요한 파일 제거)
- [ ] 코드 라인 수가 30% 이상 감소
- [ ] 주석이 명확하고 과도하지 않음

---

## 예상 효과

### 코드 품질
- **가독성**: `main.py`가 800+줄에서 200줄 이하로 감소 (약 75% 단순화)
- **유지보수성**: 기능별 모듈 분리로 수정 범위 명확화
- **주석 품질**: 핵심 로직에만 명확한 설명, 자명한 코드는 주석 제거

### 성능
- **파일 생성**: Markdown 3개 파일 제거로 I/O 작업 약 75% 감소
- **디스크 사용량**: 출력 파일 크기 감소 (1개 문서당 약 50% 절감)

### 사용자 경험
- **단순성**: HTML 뷰어 하나로 모든 기능 제공, 혼란 최소화
- **문서 품질**: 최신 기능이 정확히 반영된 문서로 학습 곡선 감소

### 프로젝트 관리
- **저장소 크기**: 불필요한 파일 제거로 초기 클론 속도 개선
- **CI/CD**: 코드 복잡도 감소로 빌드/테스트 시간 단축

---

## 주의사항

### 1. 하위 호환성
- **Breaking Change**: Markdown 파일이 필요한 사용자가 있을 수 있음
- **해결책**: CHANGELOG와 README에 명확히 공지, HTML만 사용하도록 안내

### 2. 기존 사용자 데이터
- **영향 없음**: `output/` 폴더의 기존 결과물은 영향받지 않음
- 새로 생성되는 파일만 변경됨

### 3. 리팩토링 범위
- **점진적 진행**: 한 번에 모든 변경 시도 시 버그 위험
- **단계별 검증**: 파일 삭제 → Markdown 제거 → 모듈화 → 문서 정리 순으로 진행

### 4. 테스트 커버리지
- 현재 자동화 테스트가 없으므로 수동 테스트 철저히 수행 필요
- 향후 pytest 기반 테스트 스위트 추가 권장

---

## 구현 우선순위

1. **Phase 1: 파일 정리** (위험도 낮음)
   - 불필요한 파일 삭제 (`.gitattributes`, `CHANGELOG.md`, 디버그 파일)
   - `.gitignore` 보강

2. **Phase 2: Markdown 제거** (주요 변경)
   - `main.py`, `app.py`에서 Markdown 생성 코드 제거
   - 철저한 테스트 수행

3. **Phase 3: 주석 정리** (영향 최소)
   - 과도한 주석 제거
   - docstring 보강

4. **Phase 4: 문서 업데이트** (필수)
   - README, docs/* 최신화

5. **Phase 5: 모듈화** (선택적, 별도 이슈로 분리 가능)
   - `src/` 구조 도입
   - 대규모 리팩토링이므로 별도 이슈(#37 등)로 진행 권장

---

*계획 작성일: 2025-11-28*

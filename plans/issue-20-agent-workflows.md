# Issue #20: Agent Workflows 구현 계획

## 목표
반복적인 개발 작업(브랜치 정리, 테스트 실행, 계획 수립)을 자동화하여 개발 효율성을 높이고 실수를 방지하기 위해 에이전트 워크플로우를 도입합니다.

## 구현할 워크플로우

### 1. 작업 정리 (Cleanup)
- **파일명:** `.agent/workflows/cleanup.md`
- **기능:**
    - `main` 브랜치로 체크아웃
    - 원격 저장소(`origin/main`)에서 최신 변경사항 풀(Pull)
    - (선택) 기존 작업 브랜치 삭제
- **자동화:** `// turbo-all` 적용 (사용자 승인 없이 실행)

### 2. 테스트 실행 (Test)
- **파일명:** `.agent/workflows/test.md`
- **기능:**
    - 표준 예제 파일(`samples/1706.03762v7.pdf`)을 사용하여 `main.py` 실행
    - 기본 옵션(영어 -> 한국어)으로 번역 수행
- **자동화:** `// turbo-all` 적용

### 3. 새 계획 수립 (New Plan)
- **파일명:** `.agent/workflows/new-plan.md`
- **기능:**
    - 사용자로부터 이슈 번호와 설명을 입력받음 (또는 인자로 받음)
    - `plans/TEMPLATE.md` 내용을 복사하여 새로운 계획 파일(`plans/issue-[번호]-[설명].md`) 생성
    - 생성된 파일을 에디터에 열기

## 변경 대상 파일

### [NEW] .agent/workflows/cleanup.md
### [NEW] .agent/workflows/test.md
### [NEW] .agent/workflows/new-plan.md

## 검증 계획
1. **Cleanup:** 임의의 브랜치를 생성한 후 `/cleanup` 명령어로 `main` 복귀 및 브랜치 삭제 확인.
2. **Test:** `/test` 명령어로 번역 스크립트가 정상 실행되는지 확인.
3. **New Plan:** `/new-plan` (또는 유사 명령어)으로 새 계획 파일이 규격에 맞게 생성되는지 확인.

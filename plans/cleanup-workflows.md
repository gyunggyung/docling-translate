# GitHub Workflows 제거 계획

## 목표
사용되지 않고 실패만 발생하는 `.github/workflows` 디렉토리 및 내부 파일들을 제거하여 프로젝트를 정리합니다.

## 변경 사항
### [DELETE] `.github/workflows/`
- `gemini-dispatch.yml`
- `gemini-invoke.yml`
- `gemini-review.yml`
- `gemini-scheduled-triage.yml`
- `gemini-triage.yml`

## 검증 계획
- 로컬에서 디렉토리가 삭제되었는지 확인.
- GitHub에 푸시 후 해당 탭이 정리되었는지 확인 (사용자 확인).

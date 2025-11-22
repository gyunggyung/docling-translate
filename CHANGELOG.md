# 변경 이력 (Changelog)

이 문서는 `docling-translate` 프로젝트의 주요 변경 사항을 기록합니다.

## [Unreleased]

### Added
- **상세 문서화**: `docs/USAGE.md` 추가 및 `README.md` 전면 개편 (Issue #12).
- **기여 가이드 보강**: 프로젝트 아키텍처 설명 추가 (`docs/CONTRIBUTING.md`).

## [v0.2.0] - 2025-11-21

### Added
- **다양한 포맷 지원**: PDF 외 DOCX, PPTX, HTML, Image 포맷 지원 추가 (Issue #10).
- **병렬 처리 최적화**: `max_workers` 옵션을 도입하여 폴더 단위 및 문장 단위 병렬 번역 속도 대폭 개선 (Issue #3, #28).
- **웹 뷰어 개선**: Side-by-Side 뷰와 Inline 뷰 토글 기능 추가 (Issue #26).
- **이미지/표 레이아웃**: 웹 뷰어에서 이미지와 표를 전체 너비(Full Width)로 표시하여 가독성 개선 (Issue #28).

### Changed
- **구조 리팩토링**: `main.py`와 `app.py`의 중복 로직을 정리하고 역할 분리.
- **번역 엔진**: Gemini API 연동 로직 개선 및 재시도 메커니즘(Retry) 추가.

## [v0.1.0] - 2025-10-15

### Added
- **초기 출시**: `docling`을 활용한 PDF 구조 분석 및 마크다운 변환 기능.
- **기본 번역**: Google Translate 및 DeepL 엔진 지원.
- **Streamlit Web UI**: 기본적인 파일 업로드 및 뷰어 기능 제공.

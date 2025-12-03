# 기여 가이드 업데이트 계획

## 목표
- `docs/CONTRIBUTING.md`의 "프로젝트 구조 (Architecture)" 섹션을 현재의 모듈화된 구조(`src/` 폴더 기반)에 맞게 최신화합니다.

## 변경 제안

### `docs/CONTRIBUTING.md` 업데이트

기존의 단일 `translator.py` 구조 설명을 제거하고, 다음과 같이 세분화된 구조로 변경합니다.

1.  **`main.py` (CLI Entry Point)**
    - 역할: 명령줄 인수 파싱, `src.core.process_document` 호출.
2.  **`src/core.py` (Core Orchestrator)**
    - 역할: 문서 변환(Docling), 텍스트 추출, 번역 및 HTML 생성 흐름 제어.
3.  **`src/translation/` (Translation Package)**
    - 역할: 번역 엔진 추상화 및 구현.
    - 구조: `base.py` (인터페이스), `engines/` (각 엔진 구현체: Google, DeepL, OpenAI, Qwen 등).
4.  **`src/html_generator.py` (HTML Generator)**
    - 역할: 번역 결과와 원문을 결합하여 인터랙티브 HTML 생성.
5.  **`app.py` (Web Interface)**
    - 역할: Streamlit 기반 웹 UI, `src.core`를 재사용하여 기능 구현.

## 파일 변경 목록

### [MODIFY] [CONTRIBUTING.md](file:///c:/github/docling-translate/docs/CONTRIBUTING.md)
- "프로젝트 구조" 섹션 전면 수정.

## 검증 계획
- 문서를 렌더링하여 구조 설명이 명확하고 정확한지 확인.

# Issue #12: 프로젝트 문서화(DOCS) 추가 및 최신화

## 목표
최근 추가된 핵심 기능(다양한 포맷 지원, 웹 뷰어 개선, 병렬 처리 등)을 반영하여 사용자 및 기여자 문서를 전면적으로 보강합니다.
특히 `README.md`는 "AI가 쓴 느낌"을 배제하고, 개발자가 직접 작성한 듯한 깔끔하고 전문적인 톤으로 리라이팅합니다.
기술적인 세부 사항(CLI 옵션, 엔진 설정 등)은 별도의 문서 또는 상세 섹션으로 명확하게 정리합니다.

## 배경
- **현황**: `README.md`가 기능 나열식이며, 마케팅 톤의 이모지가 과도하게 사용되어 전문성이 떨어져 보일 수 있음.
- **누락된 정보**:
    - 구체적인 CLI 옵션 (`--engine`, `--max-workers` 등)에 대한 설명 부족.
    - 지원되는 5가지 포맷(PDF, DOCX, PPTX, HTML, Image)에 대한 명시 부족.
    - API 키 설정(DeepL, Gemini) 방법 안내 부재.
    - 병렬 처리가 어떻게 동작하는지(파일 단위 vs 문장 단위)에 대한 이해 필요.

## 제안 변경 사항

### 1. `README.md` (Main Entry) 전면 리라이팅

#### [MODIFY] `README.md` & `docs/README.en.md`

**디자인 원칙**:
- **Minimal & Clean**: 과도한 이모지 제거, 간결한 문장 사용.
- **Show, Don't Just Tell**: 기능 설명보다 실제 **사용 예시(Code Snippet)** 위주.
- **Professional Tone**: "완벽하게 이해하세요" 같은 과장된 표현 대신 "정확한 구조 분석과 병렬 번역을 제공합니다"와 같이 담백하게 서술.

**주요 섹션 구성**:
- **Project Title & Badges**: 로고와 라이선스 배지.
- **Overview**: `docling` 기반의 문서 번역 도구임을 한 문장으로 정의.
- **Key Features**:
    - 1:1 문장 매핑 (Side-by-Side View).
    - 다중 포맷 지원 (PDF, Office, HTML, Image).
    - 다양한 번역 엔진 (Google, DeepL, Gemini).
- **Quick Start**:
    - 설치 (`pip install -r requirements.txt`)
    - 기본 실행 (`python main.py input.pdf`)
    - 웹 UI 실행 (`streamlit run app.py`)
- **Configuration**: 환경 변수(.env) 설정 방법 (API Key).
- **Documentation Link**: 상세 사용법(`docs/USAGE.md`) 및 기여 가이드(`CONTRIBUTING.md`) 링크.

### 2. `docs/USAGE.md` (상세 사용 가이드) 신설

#### [NEW] `docs/USAGE.md`

**포함 내용**:
- **CLI Reference**: 모든 인자 설명
    - `input_path`: 파일 또는 폴더.
    - `--from`, `--to`: 언어 코드 (ISO 639-1).
    - `--engine`: `google` (기본, 무료), `deepl` (고품질), `gemini` (LLM, 문맥 파악 우수).
    - `--max-workers`: 병렬 처리 스레드 수 (기본 4). 문서가 많을수록 높이면 유리.
    - `--benchmark`: 성능 측정 모드.
- **Supported Formats Details**: 각 포맷별 변환 특이사항.
- **Engine Setup**:
    - DeepL API Key 발급 및 `.env` 설정법.
    - Google Gemini API Key 발급 및 설정법.
- **Troubleshooting**: 자주 발생하는 오류(OCR, API Quota 등) 해결책.

### 3. `docs/CONTRIBUTING.md` (기여자 가이드) 업데이트

#### [MODIFY] `docs/CONTRIBUTING.md`

**변경 내용**:
- **Architecture Overview**:
    - `main.py`: CLI 진입점 및 배치 처리 로직.
    - `translator.py`: 번역 엔진 어댑터 및 병렬 번역 로직.
    - `app.py`: Streamlit 기반 웹 인터페이스.
- **Development Workflow**: Issue -> Plan -> Implementation -> PR 흐름 설명.
- **Testing**: 로컬 테스트 방법.

### 4. 변경 이력 (Changelog) 추가

#### [NEW] `CHANGELOG.md`

- 버전별 주요 변경 사항 기록 (기존 계획 유지).

---

## 검증 계획

### 1. 가독성 및 톤앤매너 점검
- [ ] `README.md`가 모바일과 데스크톱에서 깔끔하게 렌더링되는지 확인.
- [ ] 문장이 간결하고 명확한지(번역투 방지) 검토.

### 2. 기술 정확성 검증
- [ ] `docs/USAGE.md`에 적힌 명령어를 그대로 복사해서 실행했을 때 작동하는지 확인.
- [ ] API 키가 없는 상태에서의 동작(Google Fallback) 설명이 정확한지 확인.

---

*계획 업데이트: 2025-11-22*

# Issue #51: 코드 모듈화 (Code Modularization)

## 목표 (Goal)

`src/` 폴더 구조를 도입하여 코드를 체계적으로 정리하고, 가독성과 유지보수성을 향상시킵니다.
1. `main.py`를 가벼운 CLI 진입점으로 축소합니다.
2. `translator.py`를 객체 지향(OOP) 구조로 리팩토링하여 엔진별 중복 코드를 제거하고 확장성을 높입니다.
3. `app.py`의 UI 및 로직을 분리하여 모듈화합니다.

## 배경 (Background)

- `main.py` (844줄): HTML 생성, 문서 변환, CLI 로직 혼재.
- `app.py` (692줄): UI 코드, 상태 관리, 다국어 처리(i18n), 파일 처리 로직 혼재.
- `translator.py` (488줄): 함수 기반으로 작성되어 엔진 추가 시 코드가 비대해지고 프롬프트 관리 등이 어려움.

## 변경 제안 (Proposed Changes)

### 1. `src/` 디렉토리 구조 (패키지화)

```
src/
├── __init__.py
├── config.py           # (신규) 설정 및 상수 관리
├── core.py             # (신규) 문서 처리 핵심 로직 (Orchestrator)
├── utils.py            # (신규) 공통 유틸리티 (이미지 저장 등)
├── html_generator.py   # (신규) HTML 생성 로직
├── i18n.py             # (신규) 다국어 처리 (app.py에서 분리)
├── benchmark.py        # (이동) 벤치마크 도구
└── translation/        # (신규) 번역 엔진 패키지
    ├── __init__.py     # 팩토리 패턴 구현
    ├── base.py         # (신규) BaseTranslator 추상 클래스
    ├── google.py       # (신규) GoogleTranslator
    ├── deepl.py        # (신규) DeepLTranslator
    ├── gemini.py       # (신규) GeminiTranslator
    └── openai.py       # (신규) OpenAITranslator
```

### 2. 상세 변경 내용

#### A. 번역 엔진 리팩토링 (OOP 도입)

**`src/translation/base.py`**
- `BaseTranslator` 클래스 정의
- 공통 메서드: `translate(text)`, `translate_batch(sentences)`
- 공통 프롬프트 템플릿 관리

**`src/translation/engines/*.py`**
- 각 엔진별 구현체 (`GoogleTranslator`, `DeepLTranslator` 등)
- API 클라이언트 초기화 및 에러 처리 로직 캡슐화

**`src/translation/__init__.py`**
- `create_translator(engine_name)` 팩토리 함수 제공
- 외부에서는 이 함수만 호출하여 사용

#### B. `app.py` 모듈화

**`src/i18n.py`**
- `TRANSLATIONS` 딕셔너리 이동
- `t(key)` 함수 및 언어 설정 로직 이동

**`src/ui/` (선택적) 또는 `app.py` 내부 정리**
- `app.py`는 Streamlit UI 레이아웃 구성에만 집중
- 복잡한 로직(ZIP 생성, 이미지 주입 등)은 `src/utils.py` 또는 `src/core.py`로 이동

#### C. `main.py` 축소

- CLI 인자 파싱 및 `src.core.process_document` 호출만 담당

### 3. 마이그레이션 단계

1.  **기반 마련**: `src/` 디렉토리 생성, `utils.py`, `i18n.py` 생성.
2.  **번역기 리팩토링**: `src/translation/` 패키지 구현 및 테스트.
3.  **Core 로직 분리**: `html_generator.py`, `core.py` 구현.
4.  **CLI 연결**: `main.py`가 `src` 모듈을 사용하도록 수정.
5.  **App 연결**: `app.py`가 `src` 모듈(`i18n`, `core`, `translation`)을 사용하도록 수정.

## 검증 계획 (Verification Plan)

1.  **단위 테스트 (스크립트)**:
    - `src/translation` 패키지의 각 엔진별 번역 테스트.
    - `src/i18n` 동작 테스트.
2.  **통합 테스트**:
    - CLI 명령어로 PDF 번역 실행 및 결과 확인.
    - Streamlit 앱 실행 및 기능 확인.

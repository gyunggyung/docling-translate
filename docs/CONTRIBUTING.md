# 기여 가이드 (Contributing Guide)

`docling-translate` 프로젝트에 관심을 가져주셔서 감사합니다. 여러분의 기여는 이 프로젝트를 더 유용하고 강력하게 만드는 데 큰 힘이 됩니다.

## 프로젝트 구조 (Architecture)

이 프로젝트는 `src/` 폴더를 중심으로 모듈화되어 있습니다.

### 1. `main.py` (CLI Entry Point)
- 사용자의 명령줄 입력을 파싱하고 `src.core`를 호출하여 작업을 시작합니다.
- **역할**: CLI 인수 처리, 로깅 설정, 애플리케이션 진입점.

### 2. `src/core.py` (Core Orchestrator)
- 문서 처리의 핵심 파이프라인을 관리합니다.
- **역할**:
    - `docling`을 이용한 문서 변환(`DocumentConverter`).
    - 텍스트 추출 및 번역 요청 조율.
    - 최종 결과물(HTML) 생성 요청.

### 3. `src/translation/` (Translation Package)
- 번역 로직을 담당하는 패키지입니다.
- **구조**:
    - `base.py`: 번역 엔진의 추상 기본 클래스(`BaseTranslator`) 정의. 모든 엔진은 이 클래스를 상속받아야 합니다.
    - `__init__.py`: 팩토리 패턴(`create_translator`)을 통해 엔진 인스턴스 생성.
    - **`engines/` (구현체)**:
        - **API 기반**: `GoogleTranslator` (무료/크롤링), `DeepLTranslator`, `OpenAITranslator` (GPT), `GeminiTranslator`.
        - **로컬 LLM 기반**: `QwenTranslator`, `LFM2Translator`, `YanoljaTranslator`. (`llama-cpp-python` 사용)

### 4. `src/html_generator.py` (HTML Generator)
- 번역된 텍스트와 원본 문서를 결합하여 결과물을 생성합니다.
- **역할**:
    - HTML 템플릿 관리.
    - 좌우 대조(Side-by-Side) 뷰 및 인터랙티브 기능 스크립트 주입.

### 5. `app.py` (Web Interface)
- `streamlit` 기반의 웹 애플리케이션입니다.
- **역할**:
    - 파일 업로드 및 옵션 설정 UI.
    - `src.core.process_document`를 재사용하여 번역 수행.
    - 결과 뷰어 렌더링.

## 개발 워크플로우 (Workflow)

우리는 체계적인 개발을 위해 **Plan-First** 접근 방식을 따릅니다.

1.  **Issue 생성**: 버그 제보 또는 기능 제안을 위해 GitHub Issue를 생성합니다.
2.  **Plan 작성**: `plans/` 폴더에 `issue-[번호]-[설명].md` 형식으로 계획 파일을 작성합니다. 구현할 기능의 설계, 변경할 파일, 테스트 계획을 상세히 기술합니다.
3.  **구현 (Implementation)**: 승인된 계획에 따라 코드를 작성합니다.
4.  **테스트 (Test)**: 로컬 환경에서 변경 사항을 검증합니다.
5.  **Pull Request**: 변경 사항을 PR로 제출합니다.

## 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/gyunggyung/docling-translate.git
cd docling-translate

# 가상환경 생성 (권장)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt
```

## 테스트 방법

현재 별도의 자동화된 테스트 스위트는 없으나(추후 도입 예정), 다음과 같은 방법으로 수동 테스트를 권장합니다.

1.  **CLI 테스트**: `samples/` 폴더의 예제 파일을 사용하여 정상 동작 확인.
    ```bash
    python main.py samples/1706.03762v7.pdf
    ```
2.  **Web UI 테스트**: 스트림릿 앱을 실행하여 UI 깨짐이 없는지 확인.
    ```bash
    streamlit run app.py
    ```

## 코드 스타일

- **Type Hinting**: 모든 함수에 타입 힌트를 명시하여 가독성을 높여주세요.
- **Comments**: 복잡한 로직에는 한국어 주석을 달아주세요.
- **Documentation**: 기능 변경 시 `README.md`과 `docs/README.en.md` 또는 `docs/USAGE.md`를 함께 업데이트해주세요.
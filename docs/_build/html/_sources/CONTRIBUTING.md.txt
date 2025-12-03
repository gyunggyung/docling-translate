# 기여 가이드 (Contributing Guide)

`docling-translate` 프로젝트에 관심을 가져주셔서 감사합니다. 여러분의 기여는 이 프로젝트를 더 유용하고 강력하게 만드는 데 큰 힘이 됩니다.

## 프로젝트 구조 (Architecture)

이 프로젝트는 크게 3가지 핵심 모듈로 구성되어 있습니다.

### 1. `main.py` (CLI Entry Point & Orchestrator)
- 사용자의 명령줄 입력을 파싱하고 전체 번역 파이프라인을 조율합니다.
- **역할**:
    - 파일 입출력 관리 (단일 파일 및 폴더 스캔).
    - `docling`을 이용한 문서 변환(`DocumentConverter`) 초기화.
    - 병렬 처리(`ThreadPoolExecutor`) 관리.
    - 최종 결과물(Markdown, HTML) 생성 및 저장.

### 2. `translator.py` (Translation Logic)
- 실제 텍스트 번역을 담당하며, 다양한 번역 엔진을 추상화합니다.
- **역할**:
    - **Engine Adapters**: `GoogleTranslator`, `deepl`, `google.genai` SDK를 래핑하여 통일된 인터페이스 제공.
    - **Text Processing**: `nltk`를 사용한 문장 분리(Tokenization).
    - **Bulk Translation**: 다수의 문장을 효율적으로 병렬 번역하는 로직 포함.

### 3. `app.py` (Web Interface)
- `streamlit` 기반의 웹 애플리케이션입니다.
- **역할**:
    - 파일 업로드 UI 및 옵션 선택 핸들링.
    - `main.py`의 로직을 재사용하여 번역 수행.
    - 번역 결과를 인터랙티브한 HTML/Markdown 뷰어로 렌더링.

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
    python main.py samples/1706.03762v7.pdf --max-workers 2
    ```
2.  **Web UI 테스트**: 스트림릿 앱을 실행하여 UI 깨짐이 없는지 확인.
    ```bash
    streamlit run app.py
    ```

## 코드 스타일

- **Type Hinting**: 모든 함수에 타입 힌트를 명시하여 가독성을 높여주세요.
- **Comments**: 복잡한 로직에는 한국어 주석을 달아주세요.
- **Documentation**: 기능 변경 시 `README.md` 또는 `docs/USAGE.md`를 함께 업데이트해주세요.
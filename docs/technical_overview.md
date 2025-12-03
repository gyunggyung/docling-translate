# 기술 개요 (Technical Overview)

## 아키텍처 (Architecture)

Docling Translate는 확장성과 유지보수성을 고려한 모듈식 아키텍처를 따릅니다.

### 핵심 컴포넌트 (Core Components)

1.  **Converter (`src/converter.py`)**:
    - `docling` 라이브러리를 사용하여 PDF, DOCX, PPTX 등 다양한 문서를 로드합니다.
    - 텍스트와 레이아웃 정보를 추출합니다.
    - 문서를 번역하기 적합한 중간 형태로 변환합니다.

2.  **Translator (`src/translator.py`)**:
    - 다양한 번역 API(OpenAI, DeepL, Google Gemini) 및 로컬 LLM(Qwen, LFM2, Yanolja)과의 연동을 관리합니다.
    - API 사용량을 최적화하기 위해 텍스트를 분할하고 배치(Batch) 처리를 수행합니다.
    - 재시도 로직과 에러 처리를 구현합니다.

3.  **HTML Generator (`src/html_generator.py`)**:
    - 원문과 번역문을 입력받습니다.
    - 인터랙티브한 HTML 파일을 생성합니다.
    - 분할 뷰(Split-view) 인터페이스를 위한 JavaScript와 CSS를 포함합니다.

4.  **CLI & App (`main.py`, `app.py`)**:
    - `main.py`: 명령줄 인터페이스(CLI) 진입점입니다.
    - `app.py`: Streamlit 기반의 웹 애플리케이션입니다.

## 기술 스택 (Technologies Used)

- **Python**: 주 프로그래밍 언어.
- **Docling**: 문서 파싱 및 레이아웃 분석.
- **Streamlit**: 웹 사용자 인터페이스.
- **LangChain / OpenAI / DeepL**: AI 기반 번역.
- **BeautifulSoup**: HTML 조작 및 생성.

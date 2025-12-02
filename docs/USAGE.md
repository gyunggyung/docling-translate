# 상세 사용 가이드 (Usage Guide)

이 문서는 `docling-translate`의 상세한 사용법, 설정 방법, 그리고 트러블슈팅 가이드를 제공합니다.

## 1. 명령줄 인터페이스 (CLI)

`main.py`를 통해 터미널에서 직접 번역 작업을 수행할 수 있습니다.

### 기본 사용법

```bash
python main.py <input_path> [options]
```

- `<input_path>`: 번역할 파일(PDF, DOCX, PPTX, HTML, 이미지) 또는 폴더의 경로입니다. 폴더를 지정하면 내부의 지원되는 모든 파일을 일괄 처리합니다.

# 상세 사용 가이드 (Usage Guide)

이 문서는 `docling-translate`의 상세한 사용법, 설정 방법, 그리고 트러블슈팅 가이드를 제공합니다.

## 1. 명령줄 인터페이스 (CLI)

`main.py`를 통해 터미널에서 직접 번역 작업을 수행할 수 있습니다.

### 기본 사용법

```bash
python main.py <input_path> [options]
```

- `<input_path>`: 번역할 파일(PDF, DOCX, PPTX, HTML, 이미지) 또는 폴더의 경로입니다. 폴더를 지정하면 내부의 지원되는 모든 파일을 일괄 처리합니다.

### 주요 옵션

| 옵션 | 단축형 | 기본값 | 설명 |
| :--- | :--- | :--- | :--- |
| `--from` | `-f` | `en` | 원본 문서의 언어 코드 (예: `en`, `ja`, `zh`). |
| `--to` | `-t` | `ko` | 번역할 목표 언어 코드. |
| `--engine` | `-e` | `google` | 사용할 번역 엔진 (`google`, `deepl`, `gemini`, `openai`, `qwen-0.6b`, `lfm2`, `yanolja`). |
| `--max-workers` | | `4` | 병렬 처리를 위한 스레드 수. 시스템 사양에 따라 조절하세요. |
| `--benchmark` | `-b` | `False` | 번역 성능 측정 리포트를 출력합니다. |

### 사용 예시

**1. 기본 번역 (영어 -> 한국어)**
```bash
python main.py documents/paper.pdf
```

**2. 특정 언어로 번역 (영어 -> 일본어)**
```bash
python main.py documents/paper.pdf --target ja
```

**3. DeepL 엔진 사용 (고품질 번역)**
```bash
python main.py documents/contract.docx --engine deepl
```

**4. LFM2 로컬 엔진 사용 (비용 절감)**
```bash
python main.py documents/paper.pdf --engine lfm2
```

**5. 폴더 내 모든 파일 일괄 번역 (8개 스레드 병렬 처리)**
```bash
python main.py my_documents/ --max-workers 8
```

---

## 2. 웹 인터페이스 (Web UI)

명령어 사용이 익숙하지 않거나, 번역 결과를 즉시 시각적으로 확인하고 싶다면 웹 UI를 사용하세요.

### 실행 방법

```bash
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`로 접속됩니다.

### 주요 기능
- **Drag & Drop**: PDF, DOCX, PPTX, HTML, 이미지 파일을 드래그하여 업로드합니다.
- **실시간 옵션 변경**: 언어 및 번역 엔진을 UI에서 선택할 수 있습니다.
- **실시간 진행률 표시**: 문서 변환, 텍스트 추출, 번역, 이미지 저장 등 각 단계별 상세 상태와 진행률을 실시간으로 확인할 수 있습니다.
- **Interactive HTML Viewer**:
    - **읽기 모드 (Reading Mode)**: 번역문만 표시하며, 문장에 마우스를 올리면 툴팁으로 원문을 확인할 수 있습니다.
    - **검수 모드 (Inspection Mode)**: 원문과 번역문을 문장 단위로 좌우 대조하여 비교할 수 있습니다.
    - **뷰 모드 제어**: 우측 상단의 토글을 통해 읽기 모드와 검수 모드를 손쉽게 전환할 수 있습니다.
- **집중 모드 (Focus Mode)**: 사이드바와 컨트롤을 숨겨 번역 결과에만 집중할 수 있습니다.
- **Download**: 번역된 HTML 파일 또는 전체 결과(이미지 포함)를 ZIP으로 다운로드할 수 있습니다.
- **번역 기록 관리**: 이전 번역 결과를 자동으로 저장하고 불러올 수 있습니다.

---

## 3. 환경 설정 (API Key)

`google` 엔진(Google Translate)과 `qwen`, `lfm2`, `yanolja` 엔진(Local LLM)은 별도의 설정 없이 무료로 사용할 수 있지만, `deepl`, `gemini`, `openai`를 사용하려면 API 키 설정이 필요합니다.

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 아래와 같이 입력하세요.

```ini
# .env 파일 예시

# DeepL API (Free 또는 Pro)
DEEPL_API_KEY=your_deepl_api_key_here

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
# 또는
GOOGLE_API_KEY=your_google_api_key_here
```

### API 키 발급 안내
- **DeepL**: [DeepL API 가입](https://www.deepl.com/pro-api) 후 계정 설정에서 키를 확인하세요.
- **Gemini**: [Google AI Studio](https://aistudio.google.com/)에서 API 키를 생성할 수 있습니다.
- **OpenAI**: [OpenAI API Keys](https://platform.openai.com/api-keys)에서 API 키를 생성할 수 있습니다.

---

## 4. 지원되는 파일 형식

`docling` 라이브러리를 기반으로 다음 포맷들을 지원합니다.

- **PDF (`.pdf`)**: 텍스트, 표, 이미지를 포함한 레이아웃을 분석하여 번역합니다.
- **Word (`.docx`)**: 문서 구조를 유지하며 번역합니다.
- **PowerPoint (`.pptx`)**: 슬라이드 내용을 텍스트로 추출하여 번역합니다.
- **HTML (`.html`)**: 웹 페이지 형식을 마크다운으로 변환하여 번역합니다.
- **Image (`.png`, `.jpg`)**: 이미지 내 텍스트(OCR)를 추출하여 번역합니다. (OCR 품질은 이미지 해상도에 따라 달라질 수 있습니다.)

---

## 5. 트러블슈팅 (FAQ)

**Q. `pkg-config` 관련 에러가 발생합니다.**
A. `docling` 설치 시 시스템 의존성이 필요할 수 있습니다. (Linux/macOS)
```bash
# Ubuntu
sudo apt-get install pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl libpython3-dev
```

**Q. Gemini 번역이 실패하고 Google 번역으로 대체됩니다.**
A. `GEMINI_API_KEY`가 올바른지 확인하세요. 또한 Gemini API는 분당 요청 제한(Rate Limit)이 있을 수 있습니다. 잠시 후 다시 시도하거나 `--max-workers`를 줄여보세요.

**Q. 이미지가 번역되지 않습니다.**
A. 현재 버전에서는 이미지 자체를 번역(인페인팅)하는 기능은 지원하지 않으며, 이미지 내의 **텍스트를 추출**하여 마크다운 텍스트로 번역합니다. 캡션은 정상적으로 번역됩니다.

**Q. Windows에서 `qwen`, `lfm2` 등 로컬 엔진 사용 시 `llama-cpp-python` 설치 에러가 발생합니다.**
A. `llama-cpp-python`은 C++ 컴파일러가 필요합니다. [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)를 설치하고 "Desktop development with C++" 워크로드를 선택하여 설치해주세요. 설치 후 재부팅이 필요할 수 있습니다.

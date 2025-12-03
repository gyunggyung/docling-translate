# 시작하기 (Getting Started)

이 가이드는 Docling Translate를 로컬 컴퓨터에 설치하고 설정하는 방법을 안내합니다.

## 필수 조건 (Prerequisites)
- **Python 3.10 이상**
- **Git** (저장소 복제용)
- 번역 서비스 API 키 (선택 사항이지만 고품질 번역을 위해 권장):
    - OpenAI API Key
    - DeepL API Key
    - Google Gemini API Key

## 설치 (Installation)

1. **저장소 복제 (Clone Repository)**
   ```bash
   git clone https://github.com/gyunggyung/docling-translate.git
   cd docling-translate
   ```

2. **가상환경 생성 (권장)**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

## 설정 (Setup)

1. **환경 변수 설정**
   프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 API 키를 입력하세요:
   ```env
   OPENAI_API_KEY=your_openai_key
   DEEPL_API_KEY=your_deepl_key
   GEMINI_API_KEY=your_gemini_key
   ```

2. **설치 확인**
   도움말 명령어를 실행하여 설치가 잘 되었는지 확인합니다:
   ```bash
   python main.py --help
   ```

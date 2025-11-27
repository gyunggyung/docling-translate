# docling-translate

<p align="center">
  <img src="docs/logo.png" alt="docling-translate logo"/>
</p>

> **Docling 기반의 구조 보존형 문서 번역 도구**  
> PDF, DOCX, PPTX, HTML, 이미지의 구조를 유지하며 인터랙티브 비교 뷰를 제공합니다.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](requirements.txt)
[![English](https://img.shields.io/badge/lang-English-red.svg)](docs/README.en.md)

## 개요

`docling-translate`는 IBM의 [docling](https://github.com/ds4sd/docling) 라이브러리를 활용하여 문서의 복잡한 구조(표, 이미지, 다단 레이아웃)를 분석하고, 원문과 번역문을 **문장 단위로 매핑(1:1 Mapping)** 하여 제공하는 오픈소스 도구입니다.

기계 번역의 고질적인 문제인 **불완전한 문맥 전달과 오역**을 보완하기 위해 설계되었습니다. 단순한 텍스트 치환을 넘어, **Side-by-Side(좌우 대조)** 및 **Interactive(클릭 시 원문 확인)** 뷰를 제공하여 사용자가 원문을 즉시 확인하고 내용을 완벽하게 이해할 수 있도록 돕습니다.

## 주요 기능

- **다양한 포맷 지원**: `PDF`, `DOCX`, `PPTX`, `HTML`, `Image` 포맷을 **인터랙티브 뷰어(HTML)** 형태로 변환 및 번역.
- **문장 단위 병렬 번역**: 원문 한 문장, 번역문 한 문장을 정확히 매칭하여 가독성 극대화.
- **레이아웃 보존**: 문서 내의 표(Table)와 이미지(Image)를 유지하며 번역.
- **유연한 엔진 선택**: Google Translate(무료), DeepL(고품질), Gemini(문맥 이해), **OpenAI GPT-5-nano(최신 AI)** 지원.
- **고성능 처리**: 멀티스레딩(`max_workers`)을 통한 대량 문서 고속 병렬 처리.

## 빠른 시작 (Quick Start)

### 1. 설치

Python 3.10 이상 환경이 필요합니다.

```bash
git clone https://github.com/gyunggyung/docling-translate.git
cd docling-translate
pip install -r requirements.txt
```

### 2. CLI 실행

가장 기본적인 사용법입니다. PDF 파일을 지정하면 번역된 마크다운 및 인터랙티브 HTML 파일이 생성됩니다.

```bash
# 기본 번역 (영어 -> 한국어)
python main.py sample.pdf

# 옵션 사용 (DeepL 엔진, 일본어 번역)
python main.py sample.pdf --engine deepl --to ja

# OpenAI GPT-5-nano 사용
python main.py sample.pdf --engine openai --to ko
```

### API 키 설정 (선택 사항)

DeepL, Gemini, OpenAI를 사용하려면 `.env` 파일에 API 키를 설정해야 합니다.

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집에 API 키 입력
OPENAI_API_KEY=sk-proj-your-api-key-here
DEEPL_API_KEY=your-deepl-key-here
GEMINI_API_KEY=your-gemini-key-here
```

**API 키 발급 링크**:
- [OpenAI API Keys](https://platform.openai.com/api-keys) - GPT-5-nano 사용 (입력 $0.05/1M, 출력 $0.40/1M 토큰)
- [DeepL API](https://www.deepl.com/pro-api)
- [Google AI Studio](https://aistudio.google.com/app/apikey) - Gemini 사용

### 3. Web UI 실행

직관적인 웹 인터페이스를 통해 파일을 업로드하고 결과를 시각적으로 확인할 수 있습니다.

```bash
streamlit run app.py
```

## 상세 가이드

더 자세한 사용법과 설정 방법은 아래 문서를 참고하세요.

- [📖 **상세 사용 가이드 (USAGE.md)**](docs/USAGE.md): CLI 전체 옵션, API 키 설정, 포맷별 특징.
- [🛠 **기여 가이드 (CONTRIBUTING.md)**](docs/CONTRIBUTING.md): 프로젝트 구조, 개발 워크플로우, 테스트 방법.

## Acknowledgments

이 프로젝트는 [Docling](https://github.com/docling-project/docling) 라이브러리를 기반으로 합니다.

```bibtex
@techreport{Docling,
  author = {Deep Search Team},
  title = {Docling Technical Report},
  url = {https://arxiv.org/abs/2408.09869},
  year = {2024}
}
```

## 라이선스

이 프로젝트는 [Apache License 2.0](LICENSE)을 따릅니다.

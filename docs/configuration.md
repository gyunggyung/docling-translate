# 설정 가이드 (Configuration Guide)

Docling Translate는 명령줄 인수(CLI), 환경 변수(.env), 그리고 Web UI를 통해 설정할 수 있습니다.

## 1. 환경 변수 (Environment Variables)

프로젝트 루트에 `.env` 파일을 생성하여 API 키를 설정하세요. `.env.example` 파일을 복사하여 사용하면 편리합니다.

| 변수명 | 설명 | 필수 여부 |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | OpenAI API 키 (GPT 모델 사용 시) | 선택 |
| `DEEPL_API_KEY` | DeepL API 키 (DeepL 엔진 사용 시) | 선택 |
| `GEMINI_API_KEY` | Google Gemini API 키 (Gemini 엔진 사용 시) | 선택 |

> **참고:** `qwen-0.6b`, `lfm2`, `yanolja`와 같은 로컬 모델이나 `google` (Google Translate 웹 크롤링) 엔진을 사용할 때는 API 키가 필요하지 않습니다.

## 2. CLI 옵션 (CLI Options)

`python main.py --help`를 실행하면 최신 옵션을 확인할 수 있습니다.

### 기본 사용법
```bash
python main.py [input_file] [options]
```

### 옵션 목록

| 옵션 | 설명 | 기본값 | 가능한 값 |
| :--- | :--- | :--- | :--- |
| `input_file` | (필수) 입력 파일 경로 (PDF, DOCX, PPTX, HTML 등) | - | 파일 경로 |
| `--source` | 원본 언어 코드 | `en` | `en`, `ko`, `ja`, `zh` 등 |
| `--target` | 목표 언어 코드 | `ko` | `ko`, `en`, `ja`, `zh` 등 |
| `--engine` | 사용할 번역 엔진 | `google` | `google`, `deepl`, `gemini`, `openai`, `qwen-0.6b`, `lfm2`, `yanolja` |
| `--workers` | 병렬 작업자 수 (스레드 수) | `8` | `1` ~ `16` (로컬 모델은 `1` 권장) |

### 사용 예시

```bash
# 기본 실행 (영어 -> 한국어, Google 번역)
python main.py papers/sample.pdf

# DeepL 엔진으로 일본어로 번역
python main.py papers/sample.pdf --engine deepl --target ja

# 로컬 Qwen 모델 사용 (자동으로 workers=1로 설정됨)
python main.py papers/sample.pdf --engine qwen-0.6b
```

## 3. Web UI 설정

Web UI는 별도의 설정 파일 없이 사이드바에서 직관적으로 옵션을 변경할 수 있습니다.

```bash
streamlit run app.py
```

- **Language**: UI 언어 설정 (한국어/English)
- **Source/Target Language**: 번역 언어 설정
- **Translation Engine**: 사용할 번역 엔진 선택
- **Max Workers**: 병렬 처리 개수 조정

## 4. HTML 출력 커스터마이징

생성된 HTML 뷰어의 스타일이나 동작을 수정하려면 `src/html_generator.py` 파일을 참고하세요. CSS 스타일은 해당 파일 내의 `style` 태그 영역을 수정하면 됩니다.

## 5. 커뮤니티 및 지원 (Community & Support)

설정 중 문제가 발생하거나 새로운 기능 제안이 있다면 GitHub Discussions에 참여해 주세요. 자세한 지원 가이드는 [SUPPORT.md](../SUPPORT.md)를 참고하세요.

- [💬 **GitHub Discussions 바로가기**](https://github.com/gyunggyung/docling-translate/discussions)

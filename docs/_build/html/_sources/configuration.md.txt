# 설정 가이드 (Configuration Guide)

Docling Translate는 명령줄 인수와 환경 변수를 통해 설정할 수 있습니다.

## 환경 변수 (Environment Variables)

프로젝트 루트에 `.env` 파일을 생성하여 비밀 키를 설정하세요.

| 변수명 | 설명 | 필수 여부 |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | OpenAI (GPT 모델) API 키 | 아니오 (다른 엔진 사용 시) |
| `DEEPL_API_KEY` | DeepL API 키 | 아니오 (다른 엔진 사용 시) |
| `GEMINI_API_KEY` | Google Gemini API 키 | 아니오 (다른 엔진 사용 시) |

## CLI 옵션 (CLI Options)

`python main.py --help`를 실행하면 사용 가능한 모든 옵션을 볼 수 있습니다.

| 옵션 | 설명 | 기본값 |
| :--- | :--- | :--- |
| `--input_file` | 입력 PDF 파일 경로 | 필수 |
| `--output_dir` | 결과 저장 디렉토리 | `output/` |
| `--model` | 사용할 번역 모델 (예: `gpt-4o`, `deepl`) | `gpt-4o` |
| `--target_lang` | 목표 언어 코드 (예: `ko`, `en`) | `ko` |
| `--workers` | 병렬 작업자 수 (로컬 LLM 사용 시 1로 자동 조정됨) | `8` |

## HTML 출력 커스터마이징

생성된 HTML 뷰어는 `src/html_generator.py`를 수정하여 커스터마이징할 수 있습니다. CSS 스타일이나 JavaScript 동작을 필요에 맞게 변경하세요.

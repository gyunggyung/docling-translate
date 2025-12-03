# 문서 업데이트 및 커뮤니티 링크 추가 계획

## 목표
- `docs/configuration.md`를 최신 코드 베이스(`main.py`, `src/translation/engines/`)에 맞춰 업데이트합니다.
- GitHub Discussions 링크를 문서에 추가하여 커뮤니티 참여를 유도합니다.

## 변경 제안

### 1. `docs/configuration.md` 업데이트
- **환경 변수 섹션**:
    - `OPENAI_API_KEY`, `DEEPL_API_KEY`, `GEMINI_API_KEY` (또는 `GOOGLE_API_KEY`) 명시.
    - 로컬 모델(`qwen`, `lfm2`, `yanolja`)은 API 키가 필요 없음을 명시.
- **CLI 옵션 섹션**:
    - 잘못된 옵션 수정: `--model` -> `--engine`, `--target_lang` -> `--target`.
    - 누락된 옵션 추가: `--source`.
    - `input_file`이 위치 인자(Positional Argument)임을 명시.
    - `--engine`의 가능한 값 최신화 (`google`, `deepl`, `gemini`, `openai`, `qwen-0.6b`, `lfm2`, `yanolja`).
- **Web UI 설정 섹션 추가**:
    - `streamlit run app.py` 실행 시 사이드바를 통해 설정 가능함을 설명.
- **커뮤니티 섹션 추가**:
    - GitHub Discussions 링크 추가.

### 2. `README.md` 및 `docs/README.en.md` 업데이트
- **배지/링크 추가**: 문서 상단 배지 또는 'Support' 섹션에 GitHub Discussions 링크 추가.
- **Discussions 링크**: `https://github.com/gyunggyung/docling-translate/discussions`

## 파일 변경 목록

### [MODIFY] [configuration.md](file:///c:/github/docling-translate/docs/configuration.md)
- CLI 옵션 테이블 전면 수정.
- 환경 변수 설명 보완.
- Web UI 설정 방법 추가.
- Community 섹션 추가.

### [MODIFY] [README.md](file:///c:/github/docling-translate/README.md)
- Discussions 링크 추가.

### [MODIFY] [README.en.md](file:///c:/github/docling-translate/docs/README.en.md)
- Discussions 링크 추가.

## 검증 계획
- 문서를 렌더링(Markdown Preview)하여 오타 및 포맷 확인.
- 링크(`https://github.com/gyunggyung/docling-translate/discussions`)가 올바른지 확인.

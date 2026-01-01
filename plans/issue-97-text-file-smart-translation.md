# Issue #97: 텍스트 파일 번역 기능 추가

## 목표

txt, md, py, js, c, go, json, yaml 등 일반 텍스트 파일과 확장자가 없는 파일(LICENSE 등)을 업로드하여 **스마트 번역**할 수 있는 기능을 추가합니다. 파일 타입별로 번역 대상 영역을 지능적으로 선택하여 코드는 주석만, 마크다운은 코드블록 제외 등의 처리를 수행합니다.

**관련 이슈**: https://github.com/gyunggyung/docling-translate/issues/97

## 배경

현재 프로젝트는 Docling 라이브러리를 사용하여 PDF, DOCX, PPTX, HTML, 이미지만 지원합니다. 그러나 사용자들은 README.md, LICENSE, 소스 코드 파일 등의 텍스트 파일도 번역하고 싶어합니다. 

단순 텍스트 번역이 아닌 **스마트 번역**이 필요한 이유:
- 코드 파일에서 코드 자체는 번역하면 실행 불가
- 마크다운에서 코드 블록은 번역하면 의미 왜곡
- 원문은 반드시 유지하고 번역문과 함께 표시 필요

## 제안 변경 사항

### 1. 텍스트 파일 파서 모듈 (신규)

#### [NEW] [text_parser.py](file:///c:/github/docling-translate/src/text_parser.py)

**목적**: 텍스트 파일 타입별로 번역 대상 영역을 지능적으로 추출

**주요 기능**:

```python
from dataclasses import dataclass
from typing import List, Tuple
from pathlib import Path
import re

@dataclass
class TextSegment:
    """번역 가능한 텍스트 조각"""
    text: str           # 원본 텍스트
    start_pos: int      # 파일 내 시작 위치
    end_pos: int        # 파일 내 끝 위치
    translatable: bool  # 번역 대상 여부
    segment_type: str   # 'prose', 'comment', 'code', 'header', 'string' 등

class TextFileParser:
    """텍스트 파일을 파싱하여 번역 대상 영역을 추출합니다."""
    
    # 지원하는 파일 타입과 해당 파서
    PARSERS = {
        'markdown': ['md', 'markdown', 'rst'],
        'python': ['py', 'pyw'],
        'javascript': ['js', 'jsx', 'ts', 'tsx', 'mjs', 'cjs'],
        'c_family': ['c', 'h', 'cpp', 'hpp', 'cc', 'cxx', 'cs', 'java', 'kt', 'swift'],
        'go': ['go'],
        'rust': ['rs'],
        'shell': ['sh', 'bash', 'zsh', 'fish'],
        'config': ['json', 'yaml', 'yml', 'toml', 'xml'],
        'plaintext': ['txt', 'text', 'log', ''],  # 확장자 없음 포함
    }
    
    def parse(self, file_path: Path) -> List[TextSegment]:
        """파일을 파싱하여 세그먼트 리스트 반환"""
        ext = file_path.suffix.lstrip('.').lower()
        parser_type = self._detect_parser_type(ext)
        
        content = file_path.read_text(encoding='utf-8')
        
        if parser_type == 'markdown':
            return self._parse_markdown(content)
        elif parser_type == 'python':
            return self._parse_python(content)
        elif parser_type in ['javascript', 'c_family', 'go', 'rust', 'java']:
            return self._parse_c_style(content)  # // 및 /* */ 주석
        elif parser_type == 'shell':
            return self._parse_shell(content)  # # 주석
        elif parser_type == 'config':
            return self._parse_config(content)
        else:
            return self._parse_plaintext(content)
```

**파일 타입별 번역 규칙**:

| 파일 타입 | 확장자 | 번역 대상 | 제외 대상 |
|-----------|--------|-----------|-----------|
| **마크다운** | .md, .markdown, .rst | 본문, 헤더, 리스트 | 코드블록 (```), 인라인 코드 (`) |
| **파이썬** | .py | 주석 (#), 독스트링 ("""/''') | 코드 |
| **C 계열** | .c, .cpp, .h, .java, .cs, .kt, .swift | 주석 (//, /* */) | 코드 |
| **자바스크립트** | .js, .ts, .jsx, .tsx | 주석 (//, /* */) | 코드 |
| **Go** | .go | 주석 (//, /* */) | 코드 |
| **Rust** | .rs | 주석 (//, /* */, ///) | 코드 |
| **쉘 스크립트** | .sh, .bash | 주석 (#) | 코드 |
| **설정 파일** | .json, .yaml, .yml, .toml | 전체 (키 + 값) | 없음 |
| **일반 텍스트** | .txt, LICENSE, README | 전체 | 없음 |

---

### 2. 텍스트 파일 HTML 생성기 (신규)

#### [NEW] [text_html_generator.py](file:///c:/github/docling-translate/src/text_html_generator.py)

**목적**: 텍스트 파일의 번역 결과를 기존 HTML 뷰어와 동일한 형식으로 생성

**주요 기능**:
- 원문/번역문 양쪽 표시 (기존 방식 유지)
- 번역 불가 영역(코드)은 원문만 표시하고 코드 스타일로 구분
- 기존 `html_generator.py`의 CSS/JS 재사용
- 구문 하이라이팅 (선택적: Prism.js 또는 Highlight.js 사용)

```python
def generate_text_html(
    file_name: str,
    segments: List[TextSegment],
    translation_map: dict,
    output_dir: Path,
) -> str:
    """텍스트 파일 번역 결과 HTML 생성
    
    Args:
        file_name: 원본 파일명
        segments: 파싱된 텍스트 세그먼트 리스트
        translation_map: 원문 -> 번역문 매핑
        output_dir: 출력 디렉토리
    
    Returns:
        HTML 문자열
    """
    # 기존 HTML 헤더/푸터 재사용
    # 세그먼트별로:
    #   - translatable=True: 원문 + 번역문 양쪽 표시
    #   - translatable=False: 원문만 표시 (코드 스타일, 회색 배경)
```

**HTML 출력 구조**:
```html
<!-- 번역 가능한 세그먼트 (주석, 문서) -->
<div class="text-block translatable">
  <div class="src-block"># This is a comment</div>
  <div class="tgt-block"># 이것은 주석입니다</div>
</div>

<!-- 번역 불가 세그먼트 (코드) -->
<div class="text-block code-only">
  <pre><code>def hello_world():
    print("Hello")</code></pre>
</div>
```

---

### 3. 코어 모듈 확장

#### [MODIFY] [core.py](file:///c:/github/docling-translate/src/core.py)

**변경 내용**:
- `process_single_file` 함수에서 파일 타입 감지 추가
- 텍스트 파일인 경우 `process_text_file` 분기 처리
- Docling Converter 없이도 텍스트 파일 처리 가능하도록

```python
# 새로운 상수
TEXT_EXTENSIONS = {
    # 마크다운/문서
    '.md', '.markdown', '.rst', '.txt', '.text',
    # 프로그래밍 언어
    '.py', '.pyw',                    # Python
    '.js', '.jsx', '.ts', '.tsx',     # JavaScript/TypeScript
    '.c', '.h', '.cpp', '.hpp', '.cc', '.cxx',  # C/C++
    '.cs',                            # C#
    '.java', '.kt',                   # Java/Kotlin
    '.go',                            # Go
    '.rs',                            # Rust
    '.swift',                         # Swift
    '.sh', '.bash', '.zsh',           # Shell
    # 설정 파일
    '.json', '.yaml', '.yml', '.toml', '.xml',
    # 기타
    '.log', '.cfg', '.ini', '.env',
}

def is_text_file(file_path: str) -> bool:
    """텍스트 파일 여부 확인 (확장자 및 바이너리 체크)"""
    ext = Path(file_path).suffix.lower()
    if ext in TEXT_EXTENSIONS:
        return True
    # 확장자 없는 파일은 바이너리 체크
    if not ext:
        return not _is_binary(file_path)
    return False

def _is_binary(file_path: str) -> bool:
    """파일이 바이너리인지 확인 (null byte 존재 여부)"""
    with open(file_path, 'rb') as f:
        chunk = f.read(8192)
        return b'\x00' in chunk

def process_text_file(
    file_path: str,
    source_lang: str,
    target_lang: str,
    engine: str,
    max_workers: int,
    progress_cb: Optional[ProgressCallback] = None,
    ui_lang: str = "ko"
) -> dict:
    """텍스트 파일 전용 처리 파이프라인
    
    1. 파일 파싱 (세그먼트 추출)
    2. 번역 대상 세그먼트 수집
    3. 일괄 번역
    4. HTML 생성
    """
    pass
```

**process_single_file 수정**:
```python
def process_single_file(...):
    # 파일 타입 체크 추가
    if is_text_file(file_path):
        return process_text_file(
            file_path=file_path,
            source_lang=source_lang,
            target_lang=target_lang,
            engine=engine,
            max_workers=max_workers,
            progress_cb=progress_cb,
            ui_lang=ui_lang
        )
    
    # 기존 Docling 처리 로직
    doc: DoclingDocument = converter.convert(file_path).document
    ...
```

---

### 4. 웹 UI 확장

#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)

**변경 내용**:
- 파일 업로더의 `type` 목록에 텍스트 확장자 추가

```python
# 변경 전
type=["pdf", "docx", "pptx", "html", "htm", "png", "jpg", "jpeg"],

# 변경 후
type=[
    # 기존 Docling 지원
    "pdf", "docx", "pptx", "html", "htm", "png", "jpg", "jpeg",
    # 텍스트/마크다운
    "txt", "md", "markdown", "rst",
    # 프로그래밍 언어 (주석 번역)
    "py", "js", "jsx", "ts", "tsx", "c", "h", "cpp", "hpp", "cs", 
    "java", "kt", "go", "rs", "swift", "sh", "bash",
    # 설정 파일
    "json", "yaml", "yml", "toml", "xml",
],
```

> **참고**: Streamlit의 `file_uploader`는 확장자 없는 파일을 자동으로 지원합니다. 
> `type` 리스트에 없어도 파일을 드래그하면 업로드 가능합니다.

---

### 5. CLI 확장

#### [MODIFY] [main.py](file:///c:/github/docling-translate/main.py)

**변경 내용**:
- 텍스트 파일 지원 추가
- 도움말 메시지에 지원 형식 업데이트

```python
# 도움말 메시지 업데이트
HELP_TEXT = """
지원 형식:
  - 문서: PDF, DOCX, PPTX, HTML
  - 이미지: PNG, JPG, JPEG
  - 텍스트: TXT, MD, RST (전체 번역)
  - 코드: PY, JS, TS, C, CPP, GO, RS (주석만 번역)
  - 설정: JSON, YAML, TOML (전체 번역)
"""
```

---

## 검증 계획

### 1. 수동 테스트

**시나리오 1: 마크다운 파일**
- 파일: `README.md`
- 예상 결과: 
  - 본문 텍스트는 번역됨
  - 코드 블록(```python ... ```)은 원문 유지
  - 인라인 코드(`function_name`)는 원문 유지

**시나리오 2: 파이썬 파일**
- 파일: `main.py`
- 예상 결과:
  - `#` 주석과 `"""` 독스트링만 번역됨
  - 코드 자체는 원문 유지

**시나리오 3: C/C++ 파일**
- 파일: 샘플 `.c` 또는 `.cpp` 파일
- 예상 결과:
  - `//` 한 줄 주석 번역됨
  - `/* */` 여러 줄 주석 번역됨
  - 코드는 원문 유지

**시나리오 4: Go 파일**
- 파일: 샘플 `.go` 파일
- 예상 결과:
  - `//` 주석 번역됨
  - 코드는 원문 유지

**시나리오 5: 설정 파일 (JSON/YAML)**
- 파일: 샘플 `.json` 또는 `.yaml`
- 예상 결과:
  - 키와 값 모두 번역됨
  - JSON/YAML 구조는 유지

**시나리오 6: 확장자 없는 파일**
- 파일: `LICENSE`
- 예상 결과:
  - 전체 텍스트가 번역됨

**시나리오 7: 기존 PDF 파일 (회귀 테스트)**
- 파일: `samples/1706.03762v7.pdf`
- 예상 결과: 기존과 동일하게 작동 (회귀 없음)

### 2. 검증 체크리스트

- [ ] 마크다운 코드블록 제외 번역
- [ ] 마크다운 인라인 코드 제외 번역
- [ ] 파이썬 주석/독스트링만 번역
- [ ] C 계열 언어 주석만 번역 (C, C++, Java, C#, Go, Rust, Swift)
- [ ] 자바스크립트/타입스크립트 주석만 번역
- [ ] 쉘 스크립트 주석만 번역
- [ ] JSON/YAML 전체 번역 (키 + 값)
- [ ] 확장자 없는 파일 처리
- [ ] 바이너리 파일 거부
- [ ] 원문/번역문 HTML 정상 표시
- [ ] 코드 영역 스타일 구분
- [ ] 표준 샘플(`samples/1706.03762v7.pdf`)로 회귀 테스트
- [ ] 기존 기능이 정상 동작하는지 확인

---

## 예상 효과

- **사용성**: README, LICENSE, 소스 코드 등 다양한 파일 번역 가능
- **품질**: 코드는 보존하면서 주석/문서만 정확히 번역
- **확장성**: 새로운 파일 타입 파서를 쉽게 추가 가능한 구조
- **개발자 친화적**: 외국어 오픈소스 코드의 주석을 쉽게 이해 가능

---

## 주의사항

- **인코딩 문제**: UTF-8 외 인코딩 파일 처리 시 오류 가능 (chardet 사용 고려)
- **대용량 파일**: 매우 큰 텍스트 파일은 메모리 문제 발생 가능 (청크 처리 필요)
- **정규식 한계**: 복잡한 코드 구조(중첩 주석, 문자열 내 주석 등)는 완벽히 파싱 어려울 수 있음
- **JSON 번역 주의**: JSON 키를 번역하면 프로그램에서 읽을 때 문제 발생 가능 (사용자에게 경고 필요)

---

## 구현 순서

1. **Phase 1**: `text_parser.py` 구현
   - 기본 클래스 구조
   - 마크다운 파서 (코드블록, 인라인 코드 제외)
   - 파이썬 파서 (주석, 독스트링)
   - C 스타일 파서 (JS, C, C++, Go, Rust, Java 등)
   - 쉘 스크립트 파서
   - 설정 파일 파서 (JSON, YAML)
   - 일반 텍스트 파서

2. **Phase 2**: `text_html_generator.py` 구현
   - HTML 템플릿 (기존 스타일 재사용)
   - 세그먼트별 렌더링
   - 코드 영역 스타일링

3. **Phase 3**: `core.py` 수정
   - `is_text_file()` 함수
   - `process_text_file()` 함수
   - `process_single_file()` 분기 로직

4. **Phase 4**: UI/CLI 확장
   - `app.py` 파일 타입 추가
   - `main.py` 도움말 업데이트

5. **Phase 5**: 테스트 및 문서화
   - 각 파일 타입별 테스트
   - README 업데이트

---

*계획 작성일: 2026-01-01*

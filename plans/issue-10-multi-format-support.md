# Issue #10: 다양한 문서 포맷 지원 (Multi-format Support)

## 목표
PDF 뿐만 아니라 DOCX, PPTX, HTML, Image 등 Docling이 지원하는 다양한 포맷의 문서를 번역할 수 있도록 기능을 확장합니다.

## 배경
- 현재 `main.py`와 `app.py`는 PDF 파일(`*.pdf`)만 처리하도록 하드코딩되어 있습니다.
- Docling v2는 다양한 포맷을 지원하므로, 이를 활용하여 번역 대상을 확장하고자 합니다.
- Issue #10 요청 사항: "Pdf 뿐 아니라 txt, ppt, docs 등 여러 포맷 번역 지원"

## 제안 변경 사항

### 1. `main.py` 수정

#### [MODIFY] [main.py](file:///mnt/c/github/docling-translate/main.py)

**변경 내용**:
- `docling` 관련 임포트 추가 (`InputFormat`, `WordFormatOption`, `PowerpointFormatOption`, `HTMLFormatOption` 등).
- `process_document` 함수 내 `DocumentConverter` 초기화 로직 수정.
    - 특정 포맷(`InputFormat.PDF`)만 지정하던 방식을 확장하여, 지원하는 모든 포맷에 대한 옵션을 설정하거나 기본값을 사용하도록 변경.
    - `pipeline_options`는 PDF에만 적용되므로, 다른 포맷용 옵션(예: `WordFormatOption`)을 적절히 구성.
- `main` 함수에서 파일 탐색 로직 수정.
    - `*.pdf`만 찾던 것을 `*.docx`, `*.pptx`, `*.html` 등으로 확장.

**핵심 코드 (예시)**:
```python
from docling.datamodel.base_models import InputFormat
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
    PowerpointFormatOption,
    HTMLFormatOption,
    ImageFormatOption
)

def process_document(..., force_full_page_ocr=False, ...):
    # ... (기존 pipeline_options 설정)

    # 다양한 포맷 지원 설정
    converter = DocumentConverter(
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.DOCX,
            InputFormat.PPTX,
            InputFormat.HTML,
            InputFormat.IMAGE
        ],
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
            InputFormat.DOCX: WordFormatOption(),
            InputFormat.PPTX: PowerpointFormatOption(),
            InputFormat.HTML: HTMLFormatOption(),
            InputFormat.IMAGE: ImageFormatOption()
        }
    )
    # ...
```

### 2. `app.py` 수정

#### [MODIFY] [app.py](file:///mnt/c/github/docling-translate/app.py)

**변경 내용**:
- `st.file_uploader`의 `type` 파라미터에 `docx`, `pptx`, `html`, `png`, `jpg` 등 추가.
- 임시 파일 저장 시 원본 파일의 확장자를 유지하도록 `suffix` 파라미터 설정 (Docling이 확장자로 포맷을 감지하므로 중요).

**핵심 코드 (예시)**:
```python
uploaded_files = st.file_uploader(
    "문서 업로드 (PDF, DOCX, PPTX, HTML, Image)", 
    type=["pdf", "docx", "pptx", "html", "png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

# ...

# 임시 파일 저장 시 확장자 유지
suffix = Path(uploaded_file.name).suffix
with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
    tmp_file.write(uploaded_file.getvalue())
    tmp_path = tmp_file.name
```

## 검증 계획

### 1. 수동 테스트
- **CLI 테스트**:
    - 샘플 DOCX, PPTX 파일을 준비.
    - `python main.py samples/test.docx` 실행하여 정상 변환 및 번역 여부 확인.
- **Web UI 테스트**:
    - `streamlit run app.py` 실행.
    - DOCX, PPTX, HTML 등 다양한 파일을 업로드하여 번역이 진행되는지 확인.
    - 결과물(Markdown, HTML)에 내용이 정상적으로 포함되어 있는지 확인.

### 2. 검증 체크리스트
- [ ] PDF 이외의 파일(DOCX, PPTX 등)을 CLI로 처리할 수 있는가?
- [ ] Web UI에서 다양한 확장자의 파일을 업로드할 수 있는가?
- [ ] Docling이 파일 포맷을 올바르게 인식하고 변환하는가?
- [ ] 번역 결과물이 정상적으로 생성되는가?

---

## 예상 효과
- 사용자가 다양한 형태의 기술 문서(논문, 발표 자료, 매뉴얼 등)를 형변환 없이 바로 번역할 수 있어 편의성이 대폭 향상됨.

## 주의사항
- 이미지 파일(Scanned PDF 포함)의 경우 OCR 처리 시간이 길어질 수 있음.
- 각 포맷별로 `docling`의 추가 의존성(예: `python-docx` 등)이 필요할 수 있으나, `docling` 패키지 설치 시 대부분 포함되어 있을 것으로 예상됨. 만약 에러 발생 시 `requirements.txt` 확인 필요.

*계획 작성일: 2025-11-22*

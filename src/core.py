"""
src/core.py
===========
문서 처리의 핵심 로직을 담당하는 모듈입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **문서 변환**: Docling을 사용하여 PDF, DOCX 등의 문서를 구조화된 데이터로 변환합니다.
2.  **텍스트 수집**: 변환된 문서에서 텍스트와 캡션을 추출합니다.
3.  **번역 오케스트레이션**: 추출된 텍스트를 `src.translation` 패키지를 사용하여 병렬 번역합니다.
4.  **HTML 생성**: `src.html_generator`를 사용하여 번역 결과가 포함된 인터랙티브 HTML을 생성합니다.
5.  **텍스트 파일 처리**: txt, md, py 등 텍스트 파일의 스마트 번역을 지원합니다.
"""

import os
import time
import logging
import nltk
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable
import multiprocessing

# [Issue #92] Docling CPU 병렬 처리 최적화
# Docling 및 PyTorch/OCR 라이브러리가 로드되기 전에 환경 변수 설정
try:
    # CPU 물리 코어 수 또는 논리 코어 수 확인 (가능하면 물리 코어 권장되나 multiprocessing은 논리 코어 반환)
    cpu_count = str(multiprocessing.cpu_count())
    
    # 이미 설정되어 있지 않은 경우에만 설정 (사용자 지정 값 존중)
    if "OMP_NUM_THREADS" not in os.environ:
        os.environ["OMP_NUM_THREADS"] = cpu_count
    
    # 추가 가속화 관련 환경 변수
    if "MKL_NUM_THREADS" not in os.environ:
        os.environ["MKL_NUM_THREADS"] = cpu_count
    if "TORCH_NUM_THREADS" not in os.environ:
        os.environ["TORCH_NUM_THREADS"] = cpu_count
        
    logging.info(f"[Optimization] CPU Optimization Enabled: Threads set to {cpu_count}")
except Exception as e:
    logging.warning(f"[Optimization] Failed to set CPU threads: {e}")

from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
    PowerpointFormatOption,
    HTMLFormatOption,
    ImageFormatOption
)
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling_core.types.doc import DoclingDocument, TextItem, TableItem, PictureItem

# [NEW] pypdfium2 백엔드 import (Issue #100 - 속도 최적화)
# Fast 모드에서 사용하면 3-5배 속도 향상
try:
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
    PYPDFIUM_AVAILABLE = True
except ImportError:
    PYPDFIUM_AVAILABLE = False
    logging.warning("[Speed] PyPdfiumDocumentBackend not available. Fast mode will use default backend.")

from src.benchmark import global_benchmark as bench
from src.translation import create_translator
from src.html_generator import generate_html_content
from src.utils import ensure_nltk_resources
from src.text_parser import TextFileParser, is_text_file
from src.text_html_generator import generate_text_html, get_file_type_display, generate_code_file_html

# 진행률 콜백 타입 정의 (float: 진행률 0.0~1.0, str: 상태 메시지)
ProgressCallback = Callable[[float, str], None]

def create_converter(speed_mode: str = "balanced") -> DocumentConverter:
    """
    Docling DocumentConverter를 초기화하고 반환합니다.
    
    Args:
        speed_mode: "fast" | "balanced" 
            - fast: pypdfium2 백엔드, TableFormerMode.FAST, 이미지 생성 비활성화
            - balanced: 기본 백엔드, TableFormerMode.ACCURATE, 이미지 생성 활성화
    
    Returns:
        DocumentConverter: 설정된 문서 변환기 인스턴스
    """
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    
    # [NEW] 수식 추출 활성화 (Issue #102)
    pipeline_options.do_formula_enrichment = True
    
    # [NEW] 속도 모드에 따른 설정 분기 (Issue #100)
    if speed_mode == "fast":
        # Fast 모드: pypdfium2 백엔드 + TableFormerMode.FAST만 적용
        # 이미지/해상도는 Balanced와 동일하게 유지
        pipeline_options.table_structure_options.mode = TableFormerMode.FAST
        pipeline_options.generate_picture_images = True   # 이미지 유지
        pipeline_options.generate_table_images = True     # 표 이미지 유지
        pipeline_options.images_scale = 2.0               # 고해상도 유지
    else:
        # Balanced 모드: 품질 우선 (기본값)
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        pipeline_options.generate_picture_images = True
        pipeline_options.generate_table_images = True
        pipeline_options.images_scale = 2.0  # 고해상도

    # [NEW] 속도 모드에 따른 PDF 백엔드 선택 (Issue #100)
    if speed_mode == "fast" and PYPDFIUM_AVAILABLE:
        # Fast 모드: pypdfium2 백엔드 (3-5배 속도 향상)
        pdf_format_option = PdfFormatOption(
            pipeline_options=pipeline_options,
            backend=PyPdfiumDocumentBackend
        )
    else:
        # Balanced 모드: 기본 백엔드 (docling-parse-v4)
        pdf_format_option = PdfFormatOption(pipeline_options=pipeline_options)

    return DocumentConverter(
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.DOCX,
            InputFormat.PPTX,
            InputFormat.HTML,
            InputFormat.IMAGE,
        ],
        format_options={
            InputFormat.PDF: pdf_format_option,
            InputFormat.DOCX: WordFormatOption(),
            InputFormat.PPTX: PowerpointFormatOption(),
            InputFormat.HTML: HTMLFormatOption(),
            InputFormat.IMAGE: ImageFormatOption(),
        },
    )


# UI 메시지 다국어 지원
PROGRESS_MESSAGES = {
    "ko": {
        "analyzing": "📄 문서 구조 분석 및 변환 중... ({file_name})",
        "error_search": "❌ 오류: 파일을 찾을 수 없습니다 ({file_name})",
        "error_convert": "❌ 오류: 문서 변환 실패 ({file_name})",
        "extracting": "📝 텍스트 및 캡션 추출 중... ({file_name})",
        "translating_start": "🤖 번역 시작... ({count} 문장)",
        "translating_progress": "🤖 번역 중... {msg}",
        "saving": "💾 결과 파일 생성 및 이미지 저장 중... ({file_name})",
        "saving_progress": "💾 {msg}",
        "done": "✅ 모든 작업 완료! ({file_name})"
    },
    "en": {
        "analyzing": "📄 Analyzing document structure... ({file_name})",
        "error_search": "❌ Error: File not found ({file_name})",
        "error_convert": "❌ Error: Document conversion failed ({file_name})",
        "extracting": "📝 Extracting text and captions... ({file_name})",
        "translating_start": "🤖 Starting translation... ({count} sentences)",
        "translating_progress": "🤖 Translating... {msg}",
        "saving": "💾 Generating result file and saving images... ({file_name})",
        "saving_progress": "💾 {msg}",
        "done": "✅ All tasks completed! ({file_name})"
    }
}


def process_text_file(
    file_path: str,
    source_lang: str,
    target_lang: str,
    engine: str,
    max_workers: int = 1,
    progress_cb: Optional[ProgressCallback] = None,
    ui_lang: str = "ko",
) -> dict:
    """
    텍스트 파일 전용 처리 파이프라인입니다.
    
    txt, md, py, js 등의 텍스트 파일을 파싱하여 번역 대상 영역만 추출하고,
    번역 후 인터랙티브 HTML을 생성합니다.
    
    Args:
        file_path: 처리할 텍스트 파일 경로
        source_lang: 원본 언어 코드
        target_lang: 대상 언어 코드
        engine: 번역 엔진
        max_workers: 병렬 워커 수
        progress_cb: 진행률 콜백
        ui_lang: UI 언어
        
    Returns:
        결과 정보 딕셔너리 (output_dir, html_path)
    """
    ensure_nltk_resources()
    
    msgs = PROGRESS_MESSAGES.get(ui_lang, PROGRESS_MESSAGES["ko"])
    file_name = Path(file_path).name
    
    bench.start(f"Total Process (Text): {file_name}")
    
    if progress_cb:
        progress_cb(0.05, f"📄 텍스트 파일 분석 중... ({file_name})")
    
    # 1. 파일 유효성 검사
    if not os.path.exists(file_path):
        logging.error(f"입력 파일을 찾을 수 없습니다: {file_path}")
        if progress_cb:
            progress_cb(1.0, msgs["error_search"].format(file_name=file_name))
        return {}
    
    # 2. 출력 경로 설정
    base_filename = Path(file_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("output") / f"{base_filename}_{source_lang}_to_{target_lang}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"[{file_name}] 텍스트 파일 처리 시작 (엔진: {engine})")
    
    # 3. 텍스트 파일 파싱
    if progress_cb:
        progress_cb(0.10, f"📝 파일 파싱 중... ({file_name})")
    
    parser = TextFileParser()
    try:
        segments = parser.parse(Path(file_path))
    except Exception as e:
        logging.error(f"[{file_name}] 파일 파싱 오류: {e}", exc_info=True)
        if progress_cb:
            progress_cb(1.0, f"❌ 파싱 오류: {e}")
        return {}
    
    # 번역 대상 텍스트 추출
    translatable_texts = parser.get_translatable_texts(segments)
    unique_texts = list(set(translatable_texts))
    
    logging.info(f"[{file_name}] 세그먼트 {len(segments)}개, 번역 대상 {len(unique_texts)}개")
    
    if progress_cb:
        progress_cb(0.20, msgs["translating_start"].format(count=len(unique_texts)))
    
    # 4. 번역 실행
    bench.start(f"Translation (Text): {file_name}")
    t_trans_start = time.time()
    
    TRANSLATE_BASE = 0.20
    TRANSLATE_SPAN = 0.60
    
    def _translate_progress(local_ratio: float, msg: str):
        if progress_cb:
            global_ratio = TRANSLATE_BASE + TRANSLATE_SPAN * local_ratio
            progress_cb(global_ratio, msgs["translating_progress"].format(msg=msg))
    
    translator = create_translator(engine)
    translated_results = translator.translate_batch(
        unique_texts,
        src=source_lang,
        dest=target_lang,
        max_workers=max_workers,
        progress_cb=_translate_progress
    )
    
    t_trans_end = time.time()
    
    # 번역 맵 생성
    translation_map = dict(zip(unique_texts, translated_results))
    
    bench.end(f"Translation (Text): {file_name}")
    logging.info(f"[{file_name}] 번역 완료 ({t_trans_end - t_trans_start:.2f}초)")
    
    # 5. HTML 생성
    if progress_cb:
        progress_cb(0.85, msgs["saving"].format(file_name=file_name))
    
    ext = Path(file_path).suffix.lstrip('.').lower()
    file_type = get_file_type_display(ext)
    
    # 파일 타입별 분기
    is_markdown = ext in ('md', 'markdown')
    is_code_file = ext in ('py', 'pyw', 'js', 'jsx', 'ts', 'tsx', 'c', 'h', 'cpp', 'hpp', 'cc', 'cxx', 'cs', 'java', 'kt', 'kts', 'go', 'rs', 'swift', 'sh', 'bash', 'zsh')
    
    GEN_BASE = 0.85
    GEN_SPAN = 0.15
    
    def _gen_progress(local_ratio: float, msg: str):
        if progress_cb:
            global_ratio = GEN_BASE + GEN_SPAN * local_ratio
            progress_cb(global_ratio, msgs["saving_progress"].format(msg=msg))
    
    if is_code_file:
        # 코드 파일: 원본 코드 구조 유지하면서 주석만 번역
        original_content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
        html_content = generate_code_file_html(
            file_name=file_name,
            original_content=original_content,
            segments=segments,
            translation_map=translation_map,
            file_type=file_type,
            progress_cb=_gen_progress
        )
    else:
        # 마크다운/일반 텍스트
        html_content = generate_text_html(
            file_name=file_name,
            segments=segments,
            translation_map=translation_map,
            file_type=file_type,
            is_markdown=is_markdown,
            progress_cb=_gen_progress
        )
    
    path_html = output_dir / f"{base_filename}_interactive.html"
    with open(path_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    if progress_cb:
        progress_cb(1.0, msgs["done"].format(file_name=file_name))
    
    bench.end(f"Total Process (Text): {file_name}")
    logging.info(f"[{file_name}] 텍스트 파일 처리 완료: {output_dir}")
    
    return {
        "output_dir": output_dir,
        "html_path": path_html
    }


def process_single_file(
    file_path: str,
    converter: DocumentConverter,
    source_lang: str,
    target_lang: str,
    engine: str,
    max_workers: int = 1,
    progress_cb: Optional[ProgressCallback] = None,
    ui_lang: str = "ko",
) -> dict:
    """
    단일 파일을 처리하는 핵심 파이프라인입니다.
    
    단계:
    1. 파일 유효성 검사 및 출력 디렉토리 준비
    2. Docling을 사용한 문서 변환 (PDF/DOCX 등 -> DoclingDocument)
    3. 텍스트 및 캡션 추출 (Collection)
    4. 선택한 엔진을 사용한 병렬 번역 (Translation)
    5. 번역된 내용을 포함한 인터랙티브 HTML 생성 (HTML Generation)
    
    Args:
        file_path (str): 처리할 파일의 경로
        converter (DocumentConverter): Docling 변환기 인스턴스
        source_lang (str): 원본 언어 코드 (예: 'en')
        target_lang (str): 대상 언어 코드 (예: 'ko')
        engine (str): 사용할 번역 엔진 ('google', 'deepl', 'gemini', 'openai')
        max_workers (int): 병렬 번역 시 사용할 워커 수
        progress_cb (Optional[ProgressCallback]): 진행률 업데이트 콜백 함수
        ui_lang (str): UI 표시 언어 ('ko' or 'en')

    Returns:
        dict: 결과 정보를 담은 딕셔너리 (output_dir, html_path 포함). 실패 시 빈 딕셔너리.
    """
    ensure_nltk_resources()
    
    # UI 메시지 가져오기 (기본값 ko)
    msgs = PROGRESS_MESSAGES.get(ui_lang, PROGRESS_MESSAGES["ko"])

    file_name = Path(file_path).name
    bench.start(f"Total Process: {file_name}")

    if progress_cb:
        progress_cb(0.02, msgs["analyzing"].format(file_name=file_name))

    # 0. 텍스트 파일인 경우 별도 파이프라인으로 처리
    if is_text_file(file_path):
        logging.info(f"[{file_name}] 텍스트 파일 감지됨, 텍스트 처리 파이프라인으로 전환")
        return process_text_file(
            file_path=file_path,
            source_lang=source_lang,
            target_lang=target_lang,
            engine=engine,
            max_workers=max_workers,
            progress_cb=progress_cb,
            ui_lang=ui_lang
        )
    
    # 1. 입력 파일 유효성 검사
    if not os.path.exists(file_path):
        logging.error(f"입력 파일을 찾을 수 없습니다: {file_path}")
        if progress_cb:
            progress_cb(1.0, msgs["error_search"].format(file_name=file_name))
        return {}

    # 2. 출력 경로 설정
    # 폴더명 형식: {파일명}_{출발언어}_to_{도착언어}_{타임스탬프}
    base_filename = Path(file_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("output") / f"{base_filename}_{source_lang}_to_{target_lang}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"[{file_name}] 문서 처리 시작 (엔진: {engine})")

    # 3. Docling 변환
    bench.start(f"Conversion: {file_name}")
    logging.info(f"[{file_name}] 문서 변환 중...")
    try:
        doc: DoclingDocument = converter.convert(file_path).document
    except Exception as e:
        logging.error(f"[{file_name}] 문서 변환 오류: {e}", exc_info=True)
        if progress_cb:
            progress_cb(1.0, msgs["error_convert"].format(file_name=file_name))
        return {}
    bench.end(f"Conversion: {file_name}")
    logging.info(f"[{file_name}] 문서 변환 성공.")

    if progress_cb:
        progress_cb(0.20, msgs["extracting"].format(file_name=file_name))

    # 4. 텍스트 수집 및 번역
    bench.start(f"Translation & Save: {file_name}")
    logging.info(f"[{file_name}] 텍스트 수집 및 일괄 번역 준비... (Workers: {max_workers})")

    # --- Phase 1: Collection (텍스트 수집) ---
    all_sentences = []
    doc_items = []
    
    # 문서를 순회하며 텍스트 아이템과 캡션을 수집합니다.
    for item, _ in doc.iterate_items():
        doc_items.append((item, _))
        
        if isinstance(item, TextItem):
            if item.text and item.text.strip():
                # NLTK를 사용하여 문장 단위로 분리
                sentences = nltk.sent_tokenize(item.text)
                all_sentences.extend(sentences)
        elif isinstance(item, (TableItem, PictureItem)):
            orig_caption = item.caption_text(doc)
            if orig_caption:
                all_sentences.append(orig_caption)
            
            # [NEW] 표 셀 텍스트 수집 (pandas DataFrame 활용)
            # TableItem에서 텍스트를 추출하여 번역 대상에 포함시킵니다.
            if isinstance(item, TableItem):
                try:
                    # [FIX] deprecated API 수정 (Issue #102)
                    # export_to_dataframe()에 doc 인자 추가
                    df = item.export_to_dataframe(doc)
                    # 데이터프레임의 모든 셀 값을 문자열로 변환하여 수집
                    for text in df.values.flatten():
                        if isinstance(text, str) and text.strip():
                            all_sentences.append(text)
                    # 컬럼 헤더도 수집
                    for col in df.columns:
                        if isinstance(col, str) and col.strip():
                            all_sentences.append(col)
                except Exception as e:
                    logging.warning(f"[{file_name}] 표 텍스트 추출 중 오류 발생(무시됨): {e}")

    # 중복 문장 제거 (번역 비용 절감)
    unique_sentences = list(set(all_sentences))
    logging.info(f"[{file_name}] 총 {len(all_sentences)}개 문장 수집 (고유 문장: {len(unique_sentences)}개)")

    if progress_cb:
        progress_cb(0.25, msgs["translating_start"].format(count=len(unique_sentences)))

    # --- Phase 2: Translation (번역) ---
    t_trans_start = time.time()
    
    # 진행률 계산을 위한 상수 (번역 비중 60%)
    TRANSLATE_BASE = 0.25
    TRANSLATE_SPAN = 0.60

    # 번역 엔진의 진행률 콜백 래퍼
    def _translate_progress(local_ratio: float, msg: str):
        if progress_cb:
            global_ratio = TRANSLATE_BASE + TRANSLATE_SPAN * local_ratio
            progress_cb(global_ratio, msgs["translating_progress"].format(msg=msg))

    # Translator 인스턴스 생성 및 일괄 번역 실행
    translator = create_translator(engine)
    translated_results = translator.translate_batch(
        unique_sentences,
        src=source_lang,
        dest=target_lang,
        max_workers=max_workers,
        progress_cb=_translate_progress
    )

    t_trans_end = time.time()
    
    # 원문-번역문 매핑 생성
    translation_map = dict(zip(unique_sentences, translated_results))

    # 벤치마크 통계 기록
    total_chars = sum(len(s) for s in unique_sentences)
    bench.add_stat(
        "Translation (Sentences)",
        t_trans_end - t_trans_start,
        count=len(unique_sentences),
        volume=total_chars,
        unit="chars",
    )
    logging.info(f"[{file_name}] 일괄 번역 완료 ({t_trans_end - t_trans_start:.2f}초)")

    # --- Phase 3: HTML Generation (HTML 생성) ---
    if progress_cb:
        progress_cb(0.85, msgs["saving"].format(file_name=file_name))

    path_html = output_dir / f"{base_filename}_interactive.html"
    
    # HTML 생성 시 이미지 저장 진행률 반영 (나머지 15%)
    GEN_BASE = 0.85
    GEN_SPAN = 0.15
    
    def _gen_progress(local_ratio: float, msg: str):
        if progress_cb:
            global_ratio = GEN_BASE + GEN_SPAN * local_ratio
            progress_cb(global_ratio, msgs["saving_progress"].format(msg=msg))

    html_content = generate_html_content(
        doc,
        doc_items,
        translation_map,
        output_dir,
        base_filename,
        progress_cb=_gen_progress
    )

    with open(path_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    if progress_cb:
        progress_cb(1.0, msgs["done"].format(file_name=file_name))
    
    bench.end(f"Translation & Save: {file_name}")
    bench.end(f"Total Process: {file_name}")
    logging.info(f"[{file_name}] 파일 생성 완료: {output_dir}")
    
    return {
        "output_dir": output_dir,
        "html_path": path_html
    }

def process_document(
    file_path: str,
    converter: DocumentConverter,
    source_lang: str = "en",
    dest_lang: str = "ko",
    engine: str = "google",
    max_workers: int = 8,
    progress_cb: Optional[ProgressCallback] = None,
    ui_lang: str = "ko",
) -> dict:
    """
    외부(app.py, main.py)에서 호출하기 위한 편의성 래퍼 함수입니다.
    process_single_file을 호출합니다.
    """
    return process_single_file(
        file_path=file_path,
        converter=converter,
        source_lang=source_lang,
        target_lang=dest_lang,
        engine=engine,
        max_workers=max_workers,
        progress_cb=progress_cb,
        ui_lang=ui_lang
    )

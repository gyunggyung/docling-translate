"""
src/core.py
===========
문서 처리의 핵심 로직을 담당하는 모듈입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **문서 변환**: Docling을 사용하여 PDF, DOCX 등의 문서를 구조화된 데이터로 변환합니다.
2.  **텍스트 수집**: 변환된 문서에서 텍스트와 캡션을 추출합니다.
3.  **번역 오케스트레이션**: 추출된 텍스트를 `src.translation` 패키지를 사용하여 병렬 번역합니다.
4.  **HTML 생성**: `src.html_generator`를 사용하여 번역 결과가 포함된 인터랙티브 HTML을 생성합니다.
"""

import os
import time
import logging
import nltk
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
    PowerpointFormatOption,
    HTMLFormatOption,
    ImageFormatOption
)
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling_core.types.doc import DoclingDocument, TextItem, TableItem, PictureItem

from src.benchmark import global_benchmark as bench
from src.translation import create_translator
from src.html_generator import generate_html_content
from src.utils import ensure_nltk_resources

# 진행률 콜백 타입 정의 (float: 진행률 0.0~1.0, str: 상태 메시지)
ProgressCallback = Callable[[float, str], None]

def create_converter() -> DocumentConverter:
    """
    Docling DocumentConverter를 초기화하고 반환합니다.
    
    PDF 변환 시 OCR은 비활성화하고, 테이블 구조 분석 및 이미지 추출을 활성화합니다.
    이미지 스케일은 2.0으로 설정하여 고해상도 이미지를 얻습니다.
    
    Returns:
        DocumentConverter: 설정된 문서 변환기 인스턴스
    """
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.generate_picture_images = True
    pipeline_options.generate_table_images = True
    pipeline_options.images_scale = 2.0

    return DocumentConverter(
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.DOCX,
            InputFormat.PPTX,
            InputFormat.HTML,
            InputFormat.IMAGE,
        ],
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
            InputFormat.DOCX: WordFormatOption(),
            InputFormat.PPTX: PowerpointFormatOption(),
            InputFormat.HTML: HTMLFormatOption(),
            InputFormat.IMAGE: ImageFormatOption(),
        },
    )

def process_single_file(
    file_path: str,
    converter: DocumentConverter,
    source_lang: str,
    target_lang: str,
    engine: str,
    max_workers: int = 1,
    progress_cb: Optional[ProgressCallback] = None,
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

    Returns:
        dict: 결과 정보를 담은 딕셔너리 (output_dir, html_path 포함). 실패 시 빈 딕셔너리.
    """
    ensure_nltk_resources()
    
    file_name = Path(file_path).name
    bench.start(f"Total Process: {file_name}")

    if progress_cb:
        progress_cb(0.02, f"{file_name} 준비 중...")

    # 1. 입력 파일 유효성 검사
    if not os.path.exists(file_path):
        logging.error(f"입력 파일을 찾을 수 없습니다: {file_path}")
        if progress_cb:
            progress_cb(1.0, f"{file_name} 오류: 파일을 찾을 수 없음")
        return {}

    # 2. 출력 경로 설정
    # 폴더명 형식: {파일명}_{출발언어}_to_{도착언어}_{타임스탬프}
    base_filename = Path(file_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("output") / f"{base_filename}_{source_lang}_to_{target_lang}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"[{file_name}] 문서 처리 시작 (엔진: {engine})")

    if progress_cb:
        progress_cb(0.05, f"{file_name} 출력 경로 준비 완료")

    # 3. Docling 변환
    bench.start(f"Conversion: {file_name}")
    logging.info(f"[{file_name}] 문서 변환 중...")
    try:
        doc: DoclingDocument = converter.convert(file_path).document
    except Exception as e:
        logging.error(f"[{file_name}] 문서 변환 오류: {e}", exc_info=True)
        if progress_cb:
            progress_cb(1.0, f"{file_name} 오류: 문서 변환 실패")
        return {}
    bench.end(f"Conversion: {file_name}")
    logging.info(f"[{file_name}] 문서 변환 성공.")

    if progress_cb:
        progress_cb(0.25, f"{file_name} 문서 변환 완료")

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

    # 중복 문장 제거 (번역 비용 절감)
    unique_sentences = list(set(all_sentences))
    logging.info(f"[{file_name}] 총 {len(all_sentences)}개 문장 수집 (고유 문장: {len(unique_sentences)}개)")

    if progress_cb:
        progress_cb(0.45, f"{file_name} 텍스트 수집 완료 ({len(unique_sentences)}문장)")

    # --- Phase 2: Translation (번역) ---
    t_trans_start = time.time()
    
    # 진행률 계산을 위한 상수
    TRANSLATE_BASE = 0.5
    TRANSLATE_SPAN = 0.3

    if progress_cb:
        progress_cb(TRANSLATE_BASE, f"{file_name} 번역 시작")

    # 번역 엔진의 진행률 콜백 래퍼
    def _translate_progress(local_ratio: float, msg: str):
        if progress_cb:
            global_ratio = TRANSLATE_BASE + TRANSLATE_SPAN * local_ratio
            progress_cb(global_ratio, f"{file_name} {msg}")

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
    path_html = output_dir / f"{base_filename}_interactive.html"
    
    html_content = generate_html_content(
        doc,
        doc_items,
        translation_map,
        output_dir,
        base_filename
    )

    with open(path_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    if progress_cb:
        progress_cb(1.0, f"{file_name} 처리 완료")
    
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
    )

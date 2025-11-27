# argparse: 커맨드 라인 인자를 파싱하기 위해 사용합니다.
# os: 운영 체제와 상호 작용하기 위해 사용합니다. (예: 경로 확인)
# pathlib.Path: 파일 시스템 경로를 객체 지향적으로 다루기 위해 사용합니다.
# logging: 프로그램 실행 중 정보를 기록하기 위해 사용합니다.
import time
import sys

# 1. Import Time 측정 시작
_t0_import = time.time()

import argparse
import os
from pathlib import Path
import logging
from datetime import datetime
import concurrent.futures

import html
from typing import List, Tuple
from dotenv import load_dotenv

# .env 파일 내용 환경변수로 로드
load_dotenv()

# Hugging Face Hub 관련 환경 변수 설정 (심볼릭 링크 비활성화)
os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'

# docling 라이브러리에서 필요한 클래스들을 가져옵니다.
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
from docling_core.types.doc import DoclingDocument, TextItem, TableItem, PictureItem, DocItem

# translator.py에서 구현한 번역 함수들을 가져옵니다.
from translator import translate_by_sentence, translate_text

# 벤치마크 유틸리티
from benchmark import global_benchmark as bench

# Import Time 측정 종료
_t1_import = time.time()
_import_duration = _t1_import - _t0_import

# 기본 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HTML_HEADER = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Docling Translation Result</title>
    <style>
        :root {
            --bg-color: #f4f6f8;
            --card-bg: #ffffff;
            --text-color: #222222;
            --sub-text-color: #666666;
            --border-color: #eeeeee;
            --hover-color: #eef7ff;
            --btn-bg: #ffffff;
            --btn-text: #333333;
            --btn-border: #dddddd;
            --btn-hover-bg: #f0f0f0;
            --shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        [data-theme="dark"] {
            --bg-color: #1a1a1a;
            --card-bg: #2d2d2d;
            --text-color: #e0e0e0;
            --sub-text-color: #aaaaaa;
            --border-color: #404040;
            --hover-color: #3d3d3d;
            --btn-bg: #3d3d3d;
            --btn-text: #e0e0e0;
            --btn-border: #555555;
            --btn-hover-bg: #4d4d4d;
            --shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg-color); color: var(--text-color); margin: 0; padding: 20px; transition: background 0.3s, color 0.3s; }
        
        .controls { 
            display: flex; 
            justify-content: flex-end; 
            gap: 10px; 
            margin-bottom: 20px; 
            position: sticky; 
            top: 10px; 
            z-index: 100; 
        }
        
        .btn { 
            padding: 8px 16px; 
            background: var(--btn-bg); 
            color: var(--btn-text); 
            border: 1px solid var(--btn-border); 
            border-radius: 20px; 
            cursor: pointer; 
            box-shadow: var(--shadow); 
            font-size: 0.9em;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .btn:hover { background: var(--btn-hover-bg); }
        
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: var(--card-bg); 
            box-shadow: var(--shadow); 
            border-radius: 8px; 
            overflow: hidden; 
            transition: background 0.3s;
        }
        
        /* 공통 스타일 */
        .row { border-bottom: 1px solid var(--border-color); transition: background 0.2s; }
        .row:hover { background-color: var(--hover-color); }
        .src, .tgt { padding: 14px 20px; line-height: 1.6; }
        .src { color: var(--sub-text-color); font-size: 0.95em; background-color: rgba(0,0,0,0.02); }
        .tgt { color: var(--text-color); font-weight: 500; }
        
        /* 1. Side-by-Side Mode (Default) */
        .view-mode-side .row { display: grid; grid-template-columns: 1fr 1fr; }
        .view-mode-side .src { border-right: 1px solid var(--border-color); }
        .view-mode-side .row.full-width { display: block; border-right: none; }
        
        /* 2. Inline (Expand) Mode */
        .view-mode-inline .row { display: block; }
        .view-mode-inline .src { display: none; border-left: 4px solid #ccc; margin: 0 20px 10px; border-right: none; background: rgba(0,0,0,0.05); border-radius: 4px; }
        .view-mode-inline .tgt { cursor: pointer; }
        .view-mode-inline .tgt::after { content: ' ▾'; color: var(--sub-text-color); font-size: 0.8em; }
        .view-mode-inline .row.active .src { display: block; }

        /* 이미지/표 공통 */
        .full-width { grid-column: 1 / -1; padding: 20px; text-align: center; border-bottom: 1px solid var(--border-color); }
        img { max-width: 100%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .caption { color: var(--sub-text-color); margin-top: 10px; font-style: italic; }

        /* 모바일 반응형 */
        @media (max-width: 768px) {
            .view-mode-side .row { grid-template-columns: 1fr; }
            .view-mode-side .src { border-right: none; border-bottom: 1px dashed var(--border-color); }
        }
    </style>
    <script>
        const UI_STRINGS = {
            en: {
                theme_dark: "Dark Mode",
                theme_light: "Light Mode",
                layout_side: "Side-by-Side",
                layout_inline: "Inline Expand",
                lang_ui: "한국어",
                title: "Translation Result"
            },
            ko: {
                theme_dark: "다크 모드",
                theme_light: "라이트 모드",
                layout_side: "좌우 병렬",
                layout_inline: "펼쳐 보기",
                lang_ui: "English",
                title: "번역 결과"
            }
        };

        let currentUiLang = 'ko';
        
        function init() {
            // 테마 복원
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.body.setAttribute('data-theme', savedTheme);
            
            // UI 언어 초기화
            updateUiText();
        }

        function toggleTheme() {
            const body = document.body;
            const current = body.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            body.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            updateUiText();
        }

        function toggleLayout() {
            const container = document.getElementById('content-container');
            
            if (container.classList.contains('view-mode-side')) {
                container.classList.remove('view-mode-side');
                container.classList.add('view-mode-inline');
            } else {
                container.classList.remove('view-mode-inline');
                container.classList.add('view-mode-side');
            }
            updateUiText();
        }
        
        function toggleUiLang() {
            currentUiLang = currentUiLang === 'ko' ? 'en' : 'ko';
            updateUiText();
        }

        function updateUiText() {
            const t = UI_STRINGS[currentUiLang];
            const isDark = document.body.getAttribute('data-theme') === 'dark';
            const isSide = document.getElementById('content-container').classList.contains('view-mode-side');
            
            document.getElementById('btn-theme').innerText = isDark ? t.theme_light : t.theme_dark;
            document.getElementById('btn-layout').innerText = isSide ? t.layout_inline : t.layout_side;
            document.getElementById('btn-lang').innerText = t.lang_ui;
            document.getElementById('page-title').innerText = t.title;
        }

        function toggleInline(el) {
            const container = document.getElementById('content-container');
            if (container.classList.contains('view-mode-inline')) {
                el.parentElement.classList.toggle('active');
            }
        }
        
        window.onload = init;
    </script>
</head>
<body>
    <div class="controls">
        <button id="btn-theme" class="btn" onclick="toggleTheme()">다크 모드</button>
        <button id="btn-layout" class="btn" onclick="toggleLayout()">한줄 보기</button>
        <button id="btn-lang" class="btn" onclick="toggleUiLang()">English</button>
    </div>
    <h1 id="page-title">번역 결과</h1>
    <div id="content-container" class="container view-mode-side">
"""

HTML_FOOTER = """
    </div> <!-- Close content-container -->
</body>
</html>
"""

def save_and_get_image_path(item: DocItem, doc: DoclingDocument, output_dir: Path, base_filename: str, counters: dict) -> str:
    """
    TableItem 또는 PictureItem의 이미지를 저장하고, 마크다운에서 사용할 상대 경로를 반환합니다.
    """
    t0 = time.time() # 이미지 저장 시간 측정 시작

    item_type = "table" if isinstance(item, TableItem) else "picture"
    counters[item_type] += 1
    
    image_dir = output_dir / "images"
    image_dir.mkdir(exist_ok=True)
    
    image_filename = f"{base_filename}_{item_type}_{counters[item_type]}.png"
    image_path = image_dir / image_filename
    relative_path = f"images/{image_filename}"

    try:
        img = item.get_image(doc)
        if img:
            img.save(image_path, "PNG")
            # 벤치마크: 이미지 저장 통계
            duration = time.time() - t0
            # 이미지 크기(byte)를 알 수 있다면 좋겠지만, 여기선 일단 1개로 카운트
            bench.add_stat("Image Save", duration, count=1, volume=0, unit="imgs")
            return relative_path
    except Exception as e:
        logging.warning(f"{item.self_ref}의 이미지를 저장할 수 없습니다: {e}")
    
    return ""

def process_single_file(
    pdf_path: str,
    converter: DocumentConverter,
    source_lang: str,
    target_lang: str,
    engine: str,
    max_workers: int = 1
):
    """
    단일 파일(PDF, DOCX, PPTX 등)을 처리하는 함수 (Bulk Translation 적용)
    """
    file_name = Path(pdf_path).name
    bench.start(f"Total Process: {file_name}")
    
    # 1. 입력 파일 유효성 검사
    if not os.path.exists(pdf_path):
        logging.error(f"입력 파일을 찾을 수 없습니다: {pdf_path}")
        return

    # 2. 출력 경로 설정
    base_filename = Path(pdf_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("output") / f"{base_filename}_{source_lang}_to_{target_lang}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"[{file_name}] 문서 처리 시작 (엔진: {engine})")

    # 3. Docling 변환
    bench.start(f"Conversion: {file_name}")
    logging.info(f"[{file_name}] 문서 변환 중...")
    try:
        doc: DoclingDocument = converter.convert(pdf_path).document
    except Exception as e:
        logging.error(f"[{file_name}] 문서 변환 오류: {e}", exc_info=True)
        return
    bench.end(f"Conversion: {file_name}")
    logging.info(f"[{file_name}] 문서 변환 성공.")

    # 4. 번역 및 파일 저장 (Bulk Translation Strategy)
    bench.start(f"Translation & Save: {file_name}")
    logging.info(f"[{file_name}] 텍스트 수집 및 일괄 번역 준비... (Workers: {max_workers})")

    # --- Phase 1: Collection (모든 문장 수집 + 아이템 저장) ---
    import nltk
    all_sentences = []
    doc_items = []  # 아이템들을 리스트로 저장 (두 번째 순회를 위해)
    
    # iterate_items()는 generator이므로 한 번만 순회하고 결과를 저장
    for item, _ in doc.iterate_items():
        doc_items.append((item, _))  # 나중에 사용하기 위해 저장
        
        if isinstance(item, TextItem):
            if item.text and item.text.strip():
                sentences = nltk.sent_tokenize(item.text)
                all_sentences.extend(sentences)
        elif isinstance(item, (TableItem, PictureItem)):
             orig_caption = item.caption_text(doc)
             if orig_caption:
                 all_sentences.append(orig_caption)

    # 중복 제거 (선택 사항: 번역량 줄이기 위해)
    unique_sentences = list(set(all_sentences))
    logging.info(f"[{file_name}] 총 {len(all_sentences)}개 문장 수집 (고유 문장: {len(unique_sentences)}개)")

    # --- Phase 2: Bulk Translation (일괄 병렬 번역) ---
    t_trans_start = time.time()
    
    # translator.py에 새로 추가한 함수 사용
    from translator import translate_sentences_bulk
    
    translated_results = translate_sentences_bulk(
        unique_sentences,
        src=source_lang,
        dest=target_lang,
        engine=engine,
        max_workers=max_workers
    )
    
    t_trans_end = time.time()
    
    # 번역 맵 생성 (원문 -> 번역문)
    translation_map = dict(zip(unique_sentences, translated_results))
    
    # 통계 기록
    total_chars = sum(len(s) for s in unique_sentences)
    bench.add_stat("Translation (Sentences)", t_trans_end - t_trans_start, count=len(unique_sentences), volume=total_chars, unit="chars")
    logging.info(f"[{file_name}] 일괄 번역 완료 ({t_trans_end - t_trans_start:.2f}초)")

    # --- Phase 3: Generation (파일 생성) ---
    path_src = output_dir / f"{base_filename}_{source_lang}.md"
    path_target = output_dir / f"{base_filename}_{target_lang}.md"
    path_combined = output_dir / f"{base_filename}_combined.md"
    path_html = output_dir / f"{base_filename}_interactive.html"

    counters = {"table": 0, "picture": 0}

    with open(path_src, "w", encoding="utf-8") as f_src, \
         open(path_target, "w", encoding="utf-8") as f_target, \
         open(path_combined, "w", encoding="utf-8") as f_comb, \
         open(path_html, "w", encoding="utf-8") as f_html:
        
        f_html.write(HTML_HEADER)

        # 저장해둔 아이템 리스트 사용
        for item, _ in doc_items:
            page_num_str = f"(p. {item.prov[0].page_no})" if item.prov and item.prov[0].page_no else ""

            if isinstance(item, TextItem):
                if not item.text or not item.text.strip():
                    continue
                
                # 미리 번역된 맵에서 조회
                sentences = nltk.sent_tokenize(item.text)
                sentence_pairs = []
                for s in sentences:
                    trans = translation_map.get(s, "") # 없으면 빈 문자열 (이론상 없으면 안됨)
                    sentence_pairs.append((s, trans))
                
                original_paragraph = " ".join([pair[0] for pair in sentence_pairs])
                translated_paragraph = " ".join([pair[1] for pair in sentence_pairs])

                f_src.write(f"{original_paragraph} {page_num_str}\n\n")
                f_target.write(f"{translated_paragraph} {page_num_str}\n\n")

                for orig_sent, trans_sent in sentence_pairs:
                    f_comb.write(f"**Original ({source_lang})** {page_num_str}\n\n")
                    f_comb.write(f"{orig_sent}\n\n")
                    f_comb.write(f"**Translated ({target_lang})** {page_num_str}\n\n")
                    f_comb.write(f"{trans_sent}\n\n")
                    f_comb.write("---\n")
                    
                    orig_safe = html.escape(orig_sent)
                    trans_safe = html.escape(trans_sent)
                    f_html.write(f"""
                    <div class="row">
                        <div class="src">{orig_safe} {page_num_str}</div>
                        <div class="tgt" onclick="toggleInline(this)">{trans_safe} {page_num_str}</div>
                    </div>
                    """)
                f_comb.write("\n")

            elif isinstance(item, (TableItem, PictureItem)):
                image_path = save_and_get_image_path(item, doc, output_dir, base_filename, counters)
                
                if image_path:
                    alt_text = "table" if isinstance(item, TableItem) else "image"
                    md_link = f"![{alt_text}]({image_path}) {page_num_str}\n\n"
                    
                    f_src.write(md_link)
                    f_target.write(md_link)
                    f_comb.write(md_link)
                    
                    # New HTML structure for images/tables
                    f_html.write(f"""
                    <div class="row full-width">
                        <div><img src="{image_path}" alt="{alt_text}"></div>
                    """)
                    
                    orig_caption = item.caption_text(doc)
                    if orig_caption:
                        # 캡션 번역 조회
                        trans_caption = translation_map.get(orig_caption, "")
                        
                        f_src.write(f"**Caption:** {orig_caption} {page_num_str}\n\n")
                        f_target.write(f"**Caption:** {trans_caption} {page_num_str}\n\n")
                        
                        f_comb.write(f"**Original Caption ({source_lang}):** {orig_caption} {page_num_str}\n\n")
                        f_comb.write(f"> {orig_caption}\n\n")
                        f_comb.write(f"**Translated Caption ({target_lang}):** {trans_caption} {page_num_str}\n\n")
                        f_comb.write(f"> {trans_caption}\n\n")

                        f_html.write(f'<div class="caption">{html.escape(trans_caption)}</div>\n') # Caption inside full-width row
                    
                    f_html.write(f"</div>\n") # Close the full-width row
                    f_comb.write("---\n\n")
        
        f_html.write(HTML_FOOTER)

    bench.end(f"Translation & Save: {file_name}")
    bench.end(f"Total Process: {file_name}")
    logging.info(f"[{file_name}] 파일 생성 완료: {output_dir}")
    
    # app.py에서 사용하기 위한 딕셔너리 반환
    return {
        "output_dir": output_dir,
        "html_path": path_html,
        "combined_md": path_combined
    }


def process_document(
    file_path: str, # 변경: pdf_path -> file_path
    converter: DocumentConverter, # 인자 추가
    source_lang: str = "en",
    dest_lang: str = "ko",
    engine: str = "google",
    max_workers: int = 8
) -> dict:
    """
    단일 문서(PDF, DOCX, PPTX, HTML, Image)를 번역하는 wrapper 함수 (app.py 호환용)
    
    Args:
        file_path: 문서 파일 경로 (이름은 pdf_path이지만 다양한 포맷 지원)
        converter: DocumentConverter 인스턴스
        source_lang: 원본 언어 코드
        dest_lang: 목표 언어 코드
        engine: 번역 엔진 ('google', 'deepl', 'gemini')
        max_workers: 병렬 처리 워커 수 (기본값: 8)
    
    Returns:
        dict: output_dir, html_path, combined_md를 포함하는 딕셔너리
    """
    # PDF 전용 옵션 설정은 여전히 필요할 수 있으나, converter는 외부에서 주입받음
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.generate_picture_images = True
    pipeline_options.generate_table_images = True
    pipeline_options.images_scale = 2.0
    
    # process_single_file 호출 (전달받은 converter 사용)
    return process_single_file(
        pdf_path=file_path, # 변경: pdf_path -> file_path
        converter=converter, # 전달받은 converter 사용
        source_lang=source_lang,
        target_lang=dest_lang,
        engine=engine,
        max_workers=max_workers
    )


def main():
    parser = argparse.ArgumentParser(description="문서를 문장 단위로 번역합니다. (PDF, DOCX, PPTX, HTML, Image 지원)")
    parser.add_argument("pdf_path", type=str, help="번역할 파일 또는 폴더의 경로")
    parser.add_argument('-f', '--from', dest='source_lang', type=str, default='en', help="번역할 원본 언어 코드 (기본값: en)")
    parser.add_argument('-t', '--to', dest='target_lang', type=str, default='ko', help="번역 결과물 언어 코드 (기본값: ko)")
    parser.add_argument('-e', '--engine', dest='engine', type=str, choices=['google', 'deepl', 'gemini'], default='google', help="번역 엔진 선택")
    parser.add_argument('--max-workers', type=int, default=4, help="병렬 처리를 위한 최대 워커 수 (기본값: 4)")
    
    # 벤치마크 옵션
    parser.add_argument('-b', '--benchmark', action='store_true', help="상세 벤치마크 리포트 생성")
    parser.add_argument('--sequential', action='store_true', help="병렬 처리 비활성화 (순차 실행)")

    args = parser.parse_args()
    
    # 벤치마크 활성화 설정
    bench.enabled = args.benchmark
    if bench.enabled:
        # Import Time 기록 (수동으로 추가)
        bench.add_manual_record("Import Libraries", _t0_import, _t1_import)
        
        # 실행 설정 기록
        bench.max_workers = 1 if args.sequential else args.max_workers
        bench.sequential = args.sequential
        
        logging.info(f"벤치마크 활성화됨. Import Time: {_import_duration:.2f}s")

    input_path = Path(args.pdf_path)
    pdf_files = []

    if input_path.is_dir():
        # 다양한 포맷 지원
        for ext in ["*.pdf", "*.docx", "*.pptx", "*.html", "*.png", "*.jpg", "*.jpeg"]:
            pdf_files.extend(list(input_path.glob(ext)))
        
        if not pdf_files:
            logging.warning(f"폴더 내에 지원되는 문서 파일이 없습니다: {input_path}")
            return
    else:
        pdf_files = [input_path]

    logging.info(f"총 {len(pdf_files)}개의 파일을 처리합니다.")

    # 1. Docling 초기화 (한 번만 수행) - 이제 process_document 내부에서 생성하지 않고,
    # 멀티프로세싱을 위해 converter 객체를 공유하려면 여기서 생성해서 넘겨야 하지만,
    # 현재 구조는 process_single_file 내부에서 converter를 인자로 받도록 되어 있음.
    # 그러나 process_single_file을 직접 호출하는 것이 아니라 concurrent.futures로 호출하므로,
    # converter를 미리 생성해서 넘겨주는 것이 좋음.
    
    bench.start("Initialization")
    logging.info("Docling 파이프라인 초기화 중...")
    
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.generate_picture_images = True
    pipeline_options.generate_table_images = True
    pipeline_options.images_scale = 2.0
    
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
    bench.end("Initialization")

    # 2. 실행 (병렬 vs 순차)
    bench.start("Total Batch Execution")
    
    max_workers = 1 if args.sequential else args.max_workers
    logging.info(f"실행 모드: {'순차(Sequential)' if args.sequential else '병렬(Parallel)'} (Workers: {max_workers})")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for pdf_file in pdf_files:
            futures.append(
                executor.submit(
                    process_single_file,
                    str(pdf_file),
                    converter,
                    args.source_lang,
                    args.target_lang,
                    args.engine,
                    max_workers  # 번역 병렬 처리 워커 수 전달
                )
            )
        
        # 모든 작업 완료 대기
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"작업 중 예외 발생: {e}")

    bench.end("Total Batch Execution")

    # 3. 벤치마크 리포트 출력 및 저장
    if bench.enabled:
        print(bench.report())
        bench.save_to_file("docs/BENCHMARK_LOG.md")

if __name__ == "__main__":
    main()

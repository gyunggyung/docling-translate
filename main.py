"""
Docling을 사용한 문서 번역 CLI
다양한 포맷(PDF, DOCX, PPTX, HTML, Image)을 지원하며,
문장 단위 병렬 번역을 통해 원문과 번역문을 HTML로 제공합니다.
"""
import time
import sys

# Import Time 측정 시작
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

load_dotenv()  # .env 파일 내용 환경변수로 로드

# Hugging Face Hub 관련 환경 변수 설정 (심볼릭 링크 비활성화)
os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'

# Docling 라이브러리 임포트
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
from docling_core.types.doc import DoclingDocument, TextItem, TableItem, PictureItem, DocItem, DocItemLabel

from translator import translate_by_sentence, translate_text, translate_sentences_bulk
from benchmark import global_benchmark as bench

# Import Time 측정 종료
_t1_import = time.time()
_import_duration = _t1_import - _t0_import

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
            --highlight-bg: rgba(255, 255, 0, 0.3);
            --active-bg: rgba(0, 123, 255, 0.1);
            --related-bg: rgba(0, 123, 255, 0.15); /* 하이라이트 연동 색상 */
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
            --highlight-bg: rgba(255, 255, 0, 0.3);
            --active-bg: rgba(0, 123, 255, 0.2);
            --related-bg: rgba(0, 123, 255, 0.25);
        }
        
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg-color); color: var(--text-color); margin: 0; padding: 20px; transition: background 0.3s, color 0.3s; }
        
        .controls { 
            display: flex; 
            justify-content: flex-end; 
            gap: 10px; 
            margin-bottom: 20px; 
            position: sticky; 
            top: 10px; 
            z-index: 1000; 
            background: var(--bg-color); /* 배경색 추가 */
            padding: 10px;
            border-radius: 8px;
            box-shadow: var(--shadow);
            opacity: 0.95;
            backdrop-filter: blur(5px);
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
        .btn.active { background-color: var(--active-bg); border-color: #007bff; color: #007bff; }
        
        .container { 
            max-width: 1000px; 
            margin: 0 auto; 
            background: var(--card-bg); 
            box-shadow: var(--shadow); 
            border-radius: 8px; 
            padding: 40px;
            overflow: hidden; 
            transition: background 0.3s;
        }
        
        /* --- Document Structure --- */
        .page-marker {
            border-bottom: 2px solid var(--border-color);
            color: var(--sub-text-color);
            margin: 40px 0 20px;
            padding-bottom: 5px;
            font-size: 0.85em;
            text-align: right;
            font-weight: bold;
        }
        
        .doc-header {
            margin-top: 30px;
            margin-bottom: 15px;
            color: var(--text-color);
            line-height: 1.3;
        }
        /* 헤더 스타일은 유지하되, 내부 span에 스타일 적용 */
        .doc-header .sent { font-weight: bold; display: inline; }
        .doc-header h1 .sent { font-size: 2em; }
        .doc-header h2 .sent { font-size: 1.6em; }
        .doc-header h3 .sent { font-size: 1.3em; }
        
        .doc-list-item {
            margin-left: 20px;
            margin-bottom: 8px;
            line-height: 1.6;
            display: flex;
            align-items: flex-start;
        }
        .doc-list-marker { margin-right: 8px; }

        .paragraph-row {
            margin-bottom: 20px;
            line-height: 1.8;
            position: relative;
        }
        
        /* --- Reading Mode (Default) --- */
        .src-block { display: none; } /* Hide source by default in reading mode */
        .tgt-block { color: var(--text-color); }
        
        .sent {
            cursor: pointer;
            border-radius: 3px;
            transition: background 0.2s;
        }
        .sent:hover { background-color: var(--active-bg); }
        .sent.highlight { background-color: var(--highlight-bg); }
        .sent.related-highlight { background-color: var(--related-bg); } /* 연동 하이라이트 */

        /* Tooltip-like interaction for source text in Reading Mode */
        .sent[data-src]:hover::after {
            content: attr(data-src-text);
            position: absolute;
            left: 0;
            right: 0;
            bottom: 100%;
            background: #333;
            color: #fff;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.9em;
            z-index: 1000;
            white-space: normal;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            pointer-events: none;
            margin-bottom: 5px;
        }
        
        /* --- Inspection Mode (Side-by-Side Line View) --- */
        .view-mode-inspect .paragraph-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px dashed var(--border-color);
        }
        
        .view-mode-inspect .src-block { 
            display: block; 
            color: var(--sub-text-color); 
            font-size: 0.95em;
        }
        
        .view-mode-inspect .sent {
            display: block; /* Force line break per sentence */
            margin-bottom: 8px;
            padding: 4px;
        }
        
        .view-mode-inspect .sent[data-src]:hover::after {
            display: none; /* Disable tooltip in inspection mode */
        }

        /* 이미지/표 공통 */
        .full-width { margin: 30px 0; text-align: center; }
        img { max-width: 100%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .caption { color: var(--sub-text-color); margin-top: 10px; font-style: italic; font-size: 0.9em; }

        /* 모바일 반응형 */
        @media (max-width: 768px) {
            .view-mode-inspect .paragraph-row { grid-template-columns: 1fr; }
            .container { padding: 20px; }
        }
    </style>
    <script>
        const UI_STRINGS = {
            en: {
                theme_dark: "Dark Mode",
                theme_light: "Light Mode",
                mode_read: "Reading Mode",
                mode_inspect: "Inspection Mode",
                lang_ui: "한국어",
                title: "Translation Result"
            },
            ko: {
                theme_dark: "다크 모드",
                theme_light: "라이트 모드",
                mode_read: "읽기 모드",
                mode_inspect: "검수 모드",
                lang_ui: "English",
                title: "번역 결과"
            }
        };

        let currentUiLang = 'ko';
        
        function init() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.body.setAttribute('data-theme', savedTheme);
            updateUiText();
            setupHighlighting();
        }

        function toggleTheme() {
            const body = document.body;
            const current = body.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            body.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            updateUiText();
        }

        function toggleMode() {
            // 1. Find the best anchor element (closest to top of viewport)
            const sents = document.querySelectorAll('.sent');
            let anchor = null;
            let minDist = Infinity;
            
            for (let sent of sents) {
                // Skip hidden elements
                if (sent.offsetParent === null) continue;
                
                const rect = sent.getBoundingClientRect();
                
                // Check if element is visible (or partially visible)
                if (rect.bottom > 0 && rect.top < window.innerHeight) {
                    // Calculate distance from top of viewport
                    // We prefer elements near the top (reading line)
                    const dist = Math.abs(rect.top);
                    
                    if (dist < minDist) {
                        minDist = dist;
                        anchor = sent;
                    }
                }
            }

            // Record the relative offset of the anchor before mode switch
            let initialOffset = 0;
            if (anchor) {
                initialOffset = anchor.getBoundingClientRect().top;
                
                // If anchor is a source sentence, switch to target for stability
                if (anchor.id.startsWith('src-')) {
                    const tgtId = anchor.id.replace('src-', 'tgt-');
                    const tgtEl = document.getElementById(tgtId);
                    if (tgtEl) anchor = tgtEl;
                }
            }

            // 2. Toggle Mode
            const container = document.getElementById('content-container');
            const btn = document.getElementById('btn-mode');
            
            if (container.classList.contains('view-mode-inspect')) {
                container.classList.remove('view-mode-inspect');
                btn.classList.remove('active');
            } else {
                container.classList.add('view-mode-inspect');
                btn.classList.add('active');
            }
            updateUiText();

            // 3. Restore position using offset
            if (anchor) {
                // Force layout update to get new position
                const newRect = anchor.getBoundingClientRect();
                const currentScroll = window.scrollY;
                const targetScroll = currentScroll + (newRect.top - initialOffset);
                
                window.scrollTo({
                    top: targetScroll,
                    behavior: 'auto'
                });
            }
        }
        
        function toggleUiLang() {
            currentUiLang = currentUiLang === 'ko' ? 'en' : 'ko';
            updateUiText();
        }

        function updateUiText() {
            const t = UI_STRINGS[currentUiLang];
            const isDark = document.body.getAttribute('data-theme') === 'dark';
            const isInspect = document.getElementById('content-container').classList.contains('view-mode-inspect');
            
            document.getElementById('btn-theme').innerText = isDark ? t.theme_light : t.theme_dark;
            document.getElementById('btn-mode').innerText = isInspect ? t.mode_read : t.mode_inspect;
            document.getElementById('btn-lang').innerText = t.lang_ui;
            document.getElementById('page-title').innerText = t.title;
        }

        // 양방향 하이라이트 설정
        function setupHighlighting() {
            const sents = document.querySelectorAll('.sent');
            sents.forEach(el => {
                el.addEventListener('mouseover', function() {
                    const id = this.id; // e.g., src-123-0 or tgt-123-0
                    if (!id) return;
                    
                    const parts = id.split('-');
                    const type = parts[0]; // src or tgt
                    const itemId = parts[1];
                    const idx = parts[2];
                    
                    const targetType = type === 'src' ? 'tgt' : 'src';
                    const targetId = `${targetType}-${itemId}-${idx}`;
                    
                    const targetEl = document.getElementById(targetId);
                    if (targetEl) {
                        targetEl.classList.add('related-highlight');
                    }
                });
                
                el.addEventListener('mouseout', function() {
                    const id = this.id;
                    if (!id) return;
                    
                    const parts = id.split('-');
                    const type = parts[0];
                    const itemId = parts[1];
                    const idx = parts[2];
                    
                    const targetType = type === 'src' ? 'tgt' : 'src';
                    const targetId = `${targetType}-${itemId}-${idx}`;
                    
                    const targetEl = document.getElementById(targetId);
                    if (targetEl) {
                        targetEl.classList.remove('related-highlight');
                    }
                });
            });
        }
        
        window.onload = init;
    </script>
</head>
<body>
    <div class="controls">
        <button id="btn-theme" class="btn" onclick="toggleTheme()">다크 모드</button>
        <button id="btn-mode" class="btn" onclick="toggleMode()">검수 모드</button>
        <button id="btn-lang" class="btn" onclick="toggleUiLang()">English</button>
    </div>
    <h1 id="page-title" style="text-align: center; margin-bottom: 40px;">번역 결과</h1>
    <div id="content-container" class="container">
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

    # --- Phase 3: HTML 파일 생성 ---
    path_html = output_dir / f"{base_filename}_interactive.html"
    counters = {"table": 0, "picture": 0}

    with open(path_html, "w", encoding="utf-8") as f_html:
        
        f_html.write(HTML_HEADER)

        # 저장해둔 아이템 리스트 사용
        current_page = -1
        
        for item, _ in doc_items:
            # 페이지 마커 처리
            item_page = -1
            if item.prov and item.prov[0].page_no:
                item_page = item.prov[0].page_no
            
            if item_page > 0 and item_page != current_page:
                f_html.write(f'<div class="page-marker">Page {item_page}</div>')
                current_page = item_page

            page_num_str = f"(p. {item_page})" if item_page > 0 else ""

            if isinstance(item, TextItem):
                if not item.text or not item.text.strip():
                    continue
                
                # 미리 번역된 맵에서 조회
                sentences = nltk.sent_tokenize(item.text)
                sentence_pairs = []
                for s in sentences:
                    trans = translation_map.get(s, "") # 없으면 빈 문자열
                    sentence_pairs.append((s, trans))
                
                original_paragraph = " ".join([pair[0] for pair in sentence_pairs])
                translated_paragraph = " ".join([pair[1] for pair in sentence_pairs])

                # --- HTML 생성 로직 개선 (Issue #35) ---
                
                # 1. 헤더 (Title, Section Header)
                if item.label in [DocItemLabel.TITLE, DocItemLabel.SECTION_HEADER]:
                    # 헤더는 문장 분리 없이 통으로 표시 (단, 번역은 문장 단위로 되어 있으므로 합침)
                    # 헤더 태그 결정 (TITLE -> h1, SECTION_HEADER -> h2/h3)
                    tag = "h1" if item.label == DocItemLabel.TITLE else "h2"
                    
                    # 헤더도 paragraph-row 구조를 사용하여 검수 모드 지원
                    f_html.write('<div class="paragraph-row">')
                    
                    # 원문 (검수 모드)
                    f_html.write('<div class="src-block">')
                    # 헤더는 보통 한 줄이므로 통으로 처리
                    safe_orig = html.escape(original_paragraph)
                    # ID 부여 (헤더는 문장 분리 안함)
                    f_html.write(f'<span class="sent" id="src-{id(item)}-0">{safe_orig}</span>')
                    f_html.write('</div>')
                    
                    # 번역문 (읽기 모드) - 헤더 스타일 적용
                    f_html.write('<div class="tgt-block doc-header">')
                    safe_trans = html.escape(translated_paragraph)
                    # 헤더 태그 내부에 span을 두어 하이라이트 적용
                    f_html.write(f'<{tag}><span class="sent" id="tgt-{id(item)}-0" data-src="src-{id(item)}-0" data-src-text="{safe_orig}">{safe_trans}</span></{tag}>')
                    f_html.write('</div>')
                    
                    f_html.write('</div>')
                
                # 2. 리스트 아이템
                elif item.label == DocItemLabel.LIST_ITEM:
                    f_html.write('<div class="paragraph-row doc-list-item">')
                    
                    # 원문
                    f_html.write('<div class="src-block">')
                    f_html.write('<span class="doc-list-marker">•</span>')
                    for idx, (orig, _) in enumerate(sentence_pairs):
                        safe_orig = html.escape(orig)
                        f_html.write(f'<span class="sent" id="src-{id(item)}-{idx}">{safe_orig}</span> ')
                    f_html.write('</div>')
                    
                    # 번역문
                    f_html.write('<div class="tgt-block">')
                    f_html.write('<span class="doc-list-marker">•</span>')
                    for idx, (orig, trans) in enumerate(sentence_pairs):
                        safe_orig = html.escape(orig)
                        safe_trans = html.escape(trans)
                        f_html.write(f'<span class="sent" id="tgt-{id(item)}-{idx}" data-src="src-{id(item)}-{idx}" data-src-text="{safe_orig}">{safe_trans}</span> ')
                    f_html.write('</div>')
                    
                    f_html.write('</div>')
                
                # 3. 페이지 헤더/푸터 (무시)
                elif item.label in [DocItemLabel.PAGE_HEADER, DocItemLabel.PAGE_FOOTER]:
                    continue

                # 4. 일반 본문 (Paragraph, Text 등)
                else:
                    # 문단 시작
                    f_html.write('<div class="paragraph-row">')
                    
                    # 원문 블록 (검수 모드용)
                    f_html.write('<div class="src-block">')
                    for idx, (orig, _) in enumerate(sentence_pairs):
                        safe_orig = html.escape(orig)
                        f_html.write(f'<span class="sent" id="src-{id(item)}-{idx}">{safe_orig}</span> ')
                    f_html.write('</div>')
                    
                    # 번역문 블록 (읽기 모드 메인)
                    f_html.write('<div class="tgt-block">')
                    for idx, (orig, trans) in enumerate(sentence_pairs):
                        safe_orig = html.escape(orig)
                        safe_trans = html.escape(trans)
                        # data-src-text는 툴팁용
                        f_html.write(f'<span class="sent" id="tgt-{id(item)}-{idx}" data-src="src-{id(item)}-{idx}" data-src-text="{safe_orig}">{safe_trans}</span> ')
                    f_html.write('</div>')
                    
                    f_html.write('</div>') # End paragraph-row

            elif isinstance(item, (TableItem, PictureItem)):
                image_path = save_and_get_image_path(item, doc, output_dir, base_filename, counters)
                
                if image_path:
                    alt_text = "table" if isinstance(item, TableItem) else "image"
                    
                    # HTML structure for images/tables
                    f_html.write(f"""
                    <div class="full-width">
                        <img src="{image_path}" alt="{alt_text}">
                    """)
                    
                    orig_caption = item.caption_text(doc)
                    if orig_caption:
                        # 캡션 번역 조회
                        trans_caption = translation_map.get(orig_caption, "")
                        f_html.write(f'<div class="caption">{html.escape(trans_caption)}</div>\n') 
                    
                    f_html.write(f"</div>\n")
        
        f_html.write(HTML_FOOTER)

    bench.end(f"Translation & Save: {file_name}")
    bench.end(f"Total Process: {file_name}")
    logging.info(f"[{file_name}] 파일 생성 완료: {output_dir}")
    
    # app.py에서 사용하기 위한 딕셔너리 반환
    return {
        "output_dir": output_dir,
        "html_path": path_html
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
        dict: output_dir, html_path를 포함하는 딕셔너리
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
    parser.add_argument('-e', '--engine', dest='engine', type=str, choices=['google', 'deepl', 'gemini', 'openai'], default='google', help="번역 엔진 선택")
    parser.add_argument('--max-workers', type=int, default=8, help="병렬 처리를 위한 최대 워커 수 (기본값: 8)")
    
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

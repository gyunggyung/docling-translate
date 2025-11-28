"""
src/html_generator.py
=====================
번역 결과를 인터랙티브한 HTML 파일로 생성하는 모듈입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **HTML 구조 정의**: CSS 스타일, 자바스크립트(다크 모드, 뷰 모드 전환 등)가 포함된 HTML 템플릿을 정의합니다.
2.  **컨텐츠 생성**: Docling 문서 아이템과 번역 결과를 결합하여 HTML 본문을 생성합니다.
3.  **인터랙티브 기능**: 원문-번역문 대조(Inspection Mode), 문장 하이라이트, 툴팁 등의 기능을 제공합니다.
"""

import html
import nltk
from pathlib import Path
from docling_core.types.doc import DoclingDocument, TextItem, TableItem, PictureItem, DocItemLabel
from src.utils import save_and_get_image_path

# HTML 헤더: CSS 스타일 및 자바스크립트 포함
# - 다크 모드/라이트 모드 지원
# - 읽기 모드(번역문 위주) / 검수 모드(좌우 대조) 지원
# - 문장 단위 하이라이트 및 툴팁 기능
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
            background: var(--bg-color);
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
        .sent.related-highlight { background-color: var(--related-bg); }

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
            // 1. 현재 뷰포트에서 가장 잘 보이는 앵커 요소 찾기
            const sents = document.querySelectorAll('.sent');
            let anchor = null;
            let minDist = Infinity;
            
            for (let sent of sents) {
                if (sent.offsetParent === null) continue; // 숨겨진 요소 건너뛰기
                
                const rect = sent.getBoundingClientRect();
                
                // 화면에 조금이라도 보이면 후보
                if (rect.bottom > 0 && rect.top < window.innerHeight) {
                    const dist = Math.abs(rect.top);
                    if (dist < minDist) {
                        minDist = dist;
                        anchor = sent;
                    }
                }
            }

            // 모드 전환 전 앵커의 상대 위치 저장
            let initialOffset = 0;
            if (anchor) {
                initialOffset = anchor.getBoundingClientRect().top;
                
                // 앵커가 원문이면 대응하는 번역문으로 교체 (안정성 확보)
                if (anchor.id.startsWith('src-')) {
                    const tgtId = anchor.id.replace('src-', 'tgt-');
                    const tgtEl = document.getElementById(tgtId);
                    if (tgtEl) anchor = tgtEl;
                }
            }

            // 2. 모드 토글
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

            // 3. 위치 복원
            if (anchor) {
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

        // 원문-번역문 간 양방향 하이라이트 설정
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

from typing import Optional, Callable

# 진행률 콜백 타입 정의
ProgressCallback = Callable[[float, str], None]

def generate_html_content(
    doc: DoclingDocument,
    doc_items: list,
    translation_map: dict,
    output_dir: Path,
    base_filename: str,
    progress_cb: Optional[ProgressCallback] = None
) -> str:
    """
    Docling 문서 아이템과 번역 맵을 결합하여 인터랙티브 HTML 컨텐츠를 생성합니다.
    
    Args:
        doc (DoclingDocument): 원본 문서 객체 (캡션 참조용)
        doc_items (list): (DocItem, level) 튜플 리스트
        translation_map (dict): 원문 문장 -> 번역 문장 매핑
        output_dir (Path): 이미지 저장 경로
        base_filename (str): 이미지 파일명 접두사
        progress_cb (Optional[ProgressCallback]): 진행률 콜백
        
    Returns:
        str: 완성된 HTML 문자열
    """
    html_parts = [HTML_HEADER]
    counters = {"table": 0, "picture": 0}
    current_page = -1
    
    # 이미지/테이블 저장 진행률 계산용
    total_items = len(doc_items)
    processed_count = 0

    for item, _ in doc_items:
        processed_count += 1
        
        # 진행률 업데이트 (너무 잦은 호출 방지: 10개 단위 또는 이미지 처리 시)
        is_image = isinstance(item, (TableItem, PictureItem))
        if progress_cb and (is_image or processed_count % 50 == 0):
            ratio = processed_count / total_items
            if is_image:
                progress_cb(ratio, f"이미지 저장 중... ({processed_count}/{total_items})")
            else:
                progress_cb(ratio, f"결과 생성 중... ({processed_count}/{total_items})")

        # 페이지 마커 처리
        # 페이지 마커 처리
        item_page = -1
        if item.prov and item.prov[0].page_no:
            item_page = item.prov[0].page_no
        
        if item_page > 0 and item_page != current_page:
            html_parts.append(f'<div class="page-marker">Page {item_page}</div>')
            current_page = item_page

        if isinstance(item, TextItem):
            if not item.text or not item.text.strip():
                continue
            
            # 문장 분리 및 번역 매핑
            sentences = nltk.sent_tokenize(item.text)
            sentence_pairs = []
            for s in sentences:
                trans = translation_map.get(s)
                if trans is None:
                    trans = "" # 번역 실패 시 빈 문자열 처리
                sentence_pairs.append((s, trans))
            
            # None 필터링 (안전장치)
            original_paragraph = " ".join([pair[0] for pair in sentence_pairs if pair[0] is not None])
            translated_paragraph = " ".join([pair[1] for pair in sentence_pairs if pair[1] is not None])

            # 1. 헤더 (Title, Section Header)
            if item.label in [DocItemLabel.TITLE, DocItemLabel.SECTION_HEADER]:
                tag = "h1" if item.label == DocItemLabel.TITLE else "h2"
                
                html_parts.append('<div class="paragraph-row">')
                
                # 원문 (검수 모드용)
                html_parts.append('<div class="src-block">')
                safe_orig = html.escape(original_paragraph)
                html_parts.append(f'<span class="sent" id="src-{id(item)}-0">{safe_orig}</span>')
                html_parts.append('</div>')
                
                # 번역문 (읽기 모드용)
                html_parts.append('<div class="tgt-block doc-header">')
                safe_trans = html.escape(translated_paragraph)
                html_parts.append(f'<{tag}><span class="sent" id="tgt-{id(item)}-0" data-src="src-{id(item)}-0" data-src-text="{safe_orig}">{safe_trans}</span></{tag}>')
                html_parts.append('</div>')
                
                html_parts.append('</div>')
            
            # 2. 리스트 아이템
            elif item.label == DocItemLabel.LIST_ITEM:
                html_parts.append('<div class="paragraph-row doc-list-item">')
                
                # 원문
                html_parts.append('<div class="src-block">')
                html_parts.append('<span class="doc-list-marker">•</span>')
                for idx, (orig, _) in enumerate(sentence_pairs):
                    safe_orig = html.escape(orig)
                    html_parts.append(f'<span class="sent" id="src-{id(item)}-{idx}">{safe_orig}</span> ')
                html_parts.append('</div>')
                
                # 번역문
                html_parts.append('<div class="tgt-block">')
                html_parts.append('<span class="doc-list-marker">•</span>')
                for idx, (orig, trans) in enumerate(sentence_pairs):
                    safe_orig = html.escape(orig)
                    safe_trans = html.escape(trans)
                    html_parts.append(f'<span class="sent" id="tgt-{id(item)}-{idx}" data-src="src-{id(item)}-{idx}" data-src-text="{safe_orig}">{safe_trans}</span> ')
                html_parts.append('</div>')
                
                html_parts.append('</div>')
            
            # 3. 페이지 헤더/푸터 (무시)
            elif item.label in [DocItemLabel.PAGE_HEADER, DocItemLabel.PAGE_FOOTER]:
                continue

            # 4. 일반 본문
            else:
                html_parts.append('<div class="paragraph-row">')
                
                # 원문 블록
                html_parts.append('<div class="src-block">')
                for idx, (orig, _) in enumerate(sentence_pairs):
                    safe_orig = html.escape(orig)
                    html_parts.append(f'<span class="sent" id="src-{id(item)}-{idx}">{safe_orig}</span> ')
                html_parts.append('</div>')
                
                # 번역문 블록
                html_parts.append('<div class="tgt-block">')
                for idx, (orig, trans) in enumerate(sentence_pairs):
                    safe_orig = html.escape(orig)
                    safe_trans = html.escape(trans)
                    html_parts.append(f'<span class="sent" id="tgt-{id(item)}-{idx}" data-src="src-{id(item)}-{idx}" data-src-text="{safe_orig}">{safe_trans}</span> ')
                html_parts.append('</div>')
                
                html_parts.append('</div>')

        elif isinstance(item, (TableItem, PictureItem)):
            image_path = save_and_get_image_path(item, doc, output_dir, base_filename, counters)
            
            if image_path:
                alt_text = "table" if isinstance(item, TableItem) else "image"
                
                html_parts.append(f"""
                <div class="full-width">
                    <img src="{image_path}" alt="{alt_text}">
                """)
                
                orig_caption = item.caption_text(doc)
                if orig_caption:
                    trans_caption = translation_map.get(orig_caption, "")
                    html_parts.append(f'<div class="caption">{html.escape(trans_caption)}</div>\n') 
                
                html_parts.append(f"</div>\n")
    
    html_parts.append(HTML_FOOTER)
    return "".join(html_parts)

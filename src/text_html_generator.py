"""
src/text_html_generator.py
==========================
텍스트 파일 번역 결과를 인터랙티브한 HTML 파일로 생성하는 모듈입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **HTML 구조 정의**: 기존 html_generator.py와 동일한 CSS/JS 스타일을 재사용합니다.
2.  **세그먼트별 렌더링**: 번역 가능/불가능 영역을 구분하여 표시합니다.
3.  **마크다운 렌더링**: 마크다운 파일은 실제 HTML로 렌더링합니다.
4.  **코드 하이라이팅**: 번역 불가 영역(코드)은 별도 스타일로 표시합니다.
"""

import html
import markdown
from pathlib import Path
from typing import List, Optional, Callable

from src.text_parser import TextSegment

# 진행률 콜백 타입 정의
ProgressCallback = Callable[[float, str], None]

# 마크다운 컨버터 초기화 (확장 기능 포함)
md_converter = markdown.Markdown(extensions=['fenced_code', 'tables', 'nl2br'])

# HTML 헤더: CSS 스타일 및 자바스크립트 포함
# 기존 html_generator.py와 동일한 스타일을 사용하되, 코드 영역 스타일 추가
TEXT_HTML_HEADER = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Docling Translation Result - Text File</title>
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
            --related-bg: rgba(0, 123, 255, 0.15);
            --code-bg: #f6f8fa;
            --code-border: #e1e4e8;
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
            --code-bg: #1e1e1e;
            --code-border: #3d3d3d;
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
            max-width: 1200px; 
            margin: 0 auto; 
            background: var(--card-bg); 
            box-shadow: var(--shadow); 
            border-radius: 8px; 
            padding: 40px;
            overflow: hidden; 
            transition: background 0.3s;
        }
        
        .file-info {
            background: var(--hover-color);
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            font-size: 0.9em;
        }
        .file-info .filename {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
        }
        .file-info .meta {
            color: var(--sub-text-color);
        }
        
        /* 세그먼트 블록 */
        .segment-row {
            margin-bottom: 20px;
            line-height: 1.8;
            position: relative;
        }
        
        /* 코드 블록 스타일 (번역 불가 영역) */
        .code-segment {
            background: var(--code-bg);
            border: 1px solid var(--code-border);
            border-radius: 6px;
            padding: 16px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            margin: 15px 0;
        }
        
        .code-segment .code-label {
            display: inline-block;
            background: var(--border-color);
            color: var(--sub-text-color);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            margin-bottom: 10px;
            font-family: 'Segoe UI', sans-serif;
        }
        
        /* 읽기 모드 (기본) */
        .src-block { display: none; }
        .tgt-block { color: var(--text-color); }
        
        .sent {
            cursor: pointer;
            border-radius: 3px;
            transition: background 0.2s;
        }
        .sent:hover { background-color: var(--active-bg); }
        .sent.highlight { background-color: var(--highlight-bg); }
        .sent.related-highlight { background-color: var(--related-bg); }

        /* 툴팁 */
        .sent[data-src-text]:hover::after {
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
        
        /* 검수 모드 (Side-by-Side) */
        .view-mode-inspect .segment-row:not(.code-segment-wrapper) {
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
            display: block;
            margin-bottom: 8px;
            padding: 4px;
        }
        
        .view-mode-inspect .sent[data-src]:hover::after {
            display: none;
        }

        /* 주석 스타일 */
        .comment-segment {
            color: #6a737d;
            font-style: italic;
        }
        
        .docstring-segment {
            color: #22863a;
        }

        /* 마크다운 렌더링 스타일 */
        .md-content h1 { font-size: 2em; border-bottom: 1px solid var(--border-color); padding-bottom: 0.3em; margin: 1em 0 0.5em 0; }
        .md-content h2 { font-size: 1.5em; border-bottom: 1px solid var(--border-color); padding-bottom: 0.3em; margin: 1em 0 0.5em 0; }
        .md-content h3 { font-size: 1.25em; margin: 1em 0 0.5em 0; }
        .md-content h4 { font-size: 1em; margin: 1em 0 0.5em 0; }
        .md-content p { margin: 0.5em 0; line-height: 1.8; }
        .md-content ul, .md-content ol { margin: 0.5em 0; padding-left: 2em; }
        .md-content li { margin: 0.3em 0; }
        .md-content code { 
            background: var(--code-bg); 
            padding: 2px 6px; 
            border-radius: 4px; 
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
        }
        .md-content pre { 
            background: var(--code-bg); 
            border: 1px solid var(--code-border);
            border-radius: 6px; 
            padding: 16px; 
            overflow-x: auto; 
        }
        .md-content pre code { background: transparent; padding: 0; }
        .md-content blockquote { 
            border-left: 4px solid #007bff; 
            margin: 1em 0; 
            padding: 0.5em 1em; 
            background: var(--hover-color);
            color: var(--sub-text-color);
        }
        .md-content a { color: #007bff; text-decoration: none; }
        .md-content a:hover { text-decoration: underline; }
        .md-content table { border-collapse: collapse; width: 100%; margin: 1em 0; }
        .md-content th, .md-content td { border: 1px solid var(--border-color); padding: 8px 12px; text-align: left; }
        .md-content th { background: var(--hover-color); }
        .md-content img { max-width: 100%; height: auto; }
        .md-content strong { font-weight: 600; }
        .md-content em { font-style: italic; }

        /* 모바일 반응형 */
        @media (max-width: 768px) {
            .view-mode-inspect .segment-row { grid-template-columns: 1fr; }
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
                title: "Text Translation Result"
            },
            ko: {
                theme_dark: "다크 모드",
                theme_light: "라이트 모드",
                mode_read: "읽기 모드",
                mode_inspect: "검수 모드",
                lang_ui: "English",
                title: "텍스트 번역 결과"
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

        function setupHighlighting() {
            const sents = document.querySelectorAll('.sent');
            sents.forEach(el => {
                el.addEventListener('mouseover', function() {
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
    <h1 id="page-title" style="text-align: center; margin-bottom: 40px;">텍스트 번역 결과</h1>
    <div id="content-container" class="container">
"""

TEXT_HTML_FOOTER = """
    </div> <!-- Close content-container -->
</body>
</html>
"""


def generate_text_html(
    file_name: str,
    segments: List[TextSegment],
    translation_map: dict,
    file_type: str = "text",
    is_markdown: bool = False,
    progress_cb: Optional[ProgressCallback] = None
) -> str:
    """
    텍스트 파일의 세그먼트와 번역 맵을 결합하여 인터랙티브 HTML을 생성합니다.
    
    Args:
        file_name: 원본 파일명
        segments: TextSegment 리스트
        translation_map: 원문 텍스트 -> 번역 텍스트 매핑
        file_type: 파일 타입 (표시용)
        is_markdown: 마크다운 파일 여부 (True면 HTML로 렌더링)
        progress_cb: 진행률 콜백
        
    Returns:
        완성된 HTML 문자열
    """
    html_parts = [TEXT_HTML_HEADER]
    
    # 파일 정보 표시
    segment_count = len(segments)
    translatable_count = sum(1 for s in segments if s.translatable)
    
    html_parts.append(f"""
    <div class="file-info">
        <div class="filename">📄 {html.escape(file_name)}</div>
        <div class="meta">파일 타입: {html.escape(file_type)} | 세그먼트: {segment_count}개 | 번역 대상: {translatable_count}개</div>
    </div>
    """)
    
    # 세그먼트 처리
    total_segments = len(segments)
    
    for idx, segment in enumerate(segments):
        # 진행률 업데이트
        if progress_cb and idx % 10 == 0:
            ratio = idx / total_segments if total_segments > 0 else 1.0
            progress_cb(ratio, f"HTML 생성 중... ({idx}/{total_segments})")
        
        if segment.translatable:
            # 번역 가능한 세그먼트
            html_parts.append(_render_translatable_segment(segment, translation_map, idx, is_markdown))
        else:
            # 번역 불가 세그먼트 (코드)
            html_parts.append(_render_code_segment(segment, idx))
    
    html_parts.append(TEXT_HTML_FOOTER)
    
    if progress_cb:
        progress_cb(1.0, "HTML 생성 완료")
    
    return "".join(html_parts)


def _render_translatable_segment(
    segment: TextSegment,
    translation_map: dict,
    idx: int,
    is_markdown: bool = False
) -> str:
    """
    번역 가능한 세그먼트를 HTML로 렌더링합니다.
    
    원문과 번역문을 모두 표시하며, 검수 모드에서 좌우 대조가 가능합니다.
    is_markdown=True면 마크다운을 HTML로 렌더링합니다.
    """
    original = segment.text
    translated = translation_map.get(original, original)
    
    # 세그먼트 타입에 따른 클래스 추가
    extra_class = ""
    if segment.segment_type == "comment":
        extra_class = " comment-segment"
    elif segment.segment_type == "docstring":
        extra_class = " docstring-segment"
    
    if is_markdown:
        # 마크다운을 HTML로 렌더링
        md_converter.reset()
        rendered_orig = md_converter.convert(original)
        md_converter.reset()
        rendered_trans = md_converter.convert(translated)
        
        # 원문은 data 속성에 좁은 형태로 저장 (툴팁용)
        safe_orig_attr = html.escape(original[:200] + ('...' if len(original) > 200 else ''))
        
        return f"""
    <div class="segment-row{extra_class}">
        <div class="src-block md-content">
            <div class="sent" id="src-{idx}-0">{rendered_orig}</div>
        </div>
        <div class="tgt-block md-content">
            <div class="sent" id="tgt-{idx}-0" data-src="src-{idx}-0" data-src-text="{safe_orig_attr}">{rendered_trans}</div>
        </div>
    </div>
    """
    else:
        # 일반 텍스트 (이스케이프 처리)
        safe_orig = html.escape(original)
        safe_trans = html.escape(translated)
        
        return f"""
    <div class="segment-row{extra_class}">
        <div class="src-block">
            <span class="sent" id="src-{idx}-0">{safe_orig}</span>
        </div>
        <div class="tgt-block">
            <span class="sent" id="tgt-{idx}-0" data-src="src-{idx}-0" data-src-text="{safe_orig}">{safe_trans}</span>
        </div>
    </div>
    """


def _render_code_segment(segment: TextSegment, idx: int) -> str:
    """
    번역 불가 세그먼트(코드)를 HTML로 렌더링합니다.
    
    코드 블록 스타일로 표시하며, 원문만 표시합니다.
    """
    safe_code = html.escape(segment.text)
    
    # 세그먼트 타입에 따른 라벨
    type_labels = {
        "code": "CODE",
        "code_block": "CODE BLOCK",
        "inline_code": "INLINE",
    }
    label = type_labels.get(segment.segment_type, "CODE")
    
    return f"""
    <div class="code-segment-wrapper">
        <div class="code-segment">
            <span class="code-label">{label}</span>
            <pre><code>{safe_code}</code></pre>
        </div>
    </div>
    """


def get_file_type_display(ext: str) -> str:
    """
    확장자에 따른 파일 타입 표시 문자열을 반환합니다.
    
    Args:
        ext: 파일 확장자 (점 제외)
        
    Returns:
        표시용 파일 타입 문자열
    """
    type_map = {
        # 마크다운
        "md": "Markdown",
        "markdown": "Markdown",
        "rst": "reStructuredText",
        
        # 프로그래밍 언어
        "py": "Python",
        "pyw": "Python",
        "js": "JavaScript",
        "jsx": "JavaScript (React)",
        "ts": "TypeScript",
        "tsx": "TypeScript (React)",
        "c": "C",
        "h": "C Header",
        "cpp": "C++",
        "hpp": "C++ Header",
        "cc": "C++",
        "cxx": "C++",
        "cs": "C#",
        "java": "Java",
        "kt": "Kotlin",
        "kts": "Kotlin Script",
        "go": "Go",
        "rs": "Rust",
        "swift": "Swift",
        
        # 쉘
        "sh": "Shell Script",
        "bash": "Bash Script",
        "zsh": "Zsh Script",
        
        # 설정
        "json": "JSON",
        "yaml": "YAML",
        "yml": "YAML",
        "toml": "TOML",
        "xml": "XML",
        
        # 일반
        "txt": "Plain Text",
        "text": "Plain Text",
        "log": "Log File",
    }
    
    # 확장자가 없는 경우
    if not ext:
        return "Plain Text"
    
    return type_map.get(ext.lower(), "Text File")


def generate_code_file_html(
    file_name: str,
    original_content: str,
    segments: List[TextSegment],
    translation_map: dict,
    file_type: str = "Code",
    progress_cb: Optional[ProgressCallback] = None
) -> str:
    """
    코드 파일을 원본 구조 그대로 유지하면서 주석/독스트링만 번역하여 HTML 생성.
    
    주석과 독스트링은 번역문으로 대체되고, hover 시 원문을 볼 수 있습니다.
    코드 부분은 그대로 유지되어 문맥을 잃지 않습니다.
    
    Args:
        file_name: 파일명
        original_content: 원본 파일 전체 내용
        segments: 파싱된 세그먼트 리스트
        translation_map: 원문 -> 번역문 매핑
        file_type: 파일 타입 표시
        progress_cb: 진행률 콜백
    """
    # 코드 파일용 HTML 헤더 (구문 강조 스타일 포함)
    code_html_header = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Translation - ''' + html.escape(file_name) + '''</title>
    <style>
        :root {
            --bg-color: #1e1e1e;
            --card-bg: #252526;
            --text-color: #d4d4d4;
            --sub-text-color: #808080;
            --border-color: #3c3c3c;
            --line-num-color: #858585;
            --comment-color: #6a9955;
            --string-color: #ce9178;
            --keyword-color: #569cd6;
            --function-color: #dcdcaa;
            --highlight-bg: rgba(255, 255, 0, 0.2);
        }
        [data-theme="light"] {
            --bg-color: #ffffff;
            --card-bg: #f8f8f8;
            --text-color: #333333;
            --sub-text-color: #666666;
            --border-color: #e0e0e0;
            --line-num-color: #999999;
            --comment-color: #008000;
            --string-color: #a31515;
            --keyword-color: #0000ff;
            --function-color: #795e26;
            --highlight-bg: rgba(255, 255, 0, 0.3);
        }
        
        * { box-sizing: border-box; }
        body { 
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            background: var(--bg-color); 
            color: var(--text-color); 
            margin: 0; 
            padding: 20px;
            line-height: 1.5;
        }
        
        .controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px 20px;
            background: var(--card-bg);
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }
        
        .file-info {
            font-size: 0.9em;
            color: var(--sub-text-color);
        }
        .file-info .filename {
            font-weight: bold;
            color: var(--text-color);
            margin-right: 15px;
        }
        
        .btn-group { display: flex; gap: 10px; }
        .btn {
            padding: 8px 16px;
            background: transparent;
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85em;
            transition: all 0.2s;
        }
        .btn:hover { background: var(--border-color); }
        .btn.active { background: #007acc; border-color: #007acc; color: white; }
        
        .code-container {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .code-view {
            display: flex;
            overflow-x: auto;
        }
        
        .line-numbers {
            padding: 20px 15px;
            text-align: right;
            color: var(--line-num-color);
            background: var(--bg-color);
            border-right: 1px solid var(--border-color);
            user-select: none;
            font-size: 0.85em;
        }
        
        .code-content {
            padding: 20px;
            flex: 1;
            overflow-x: auto;
            white-space: pre;
        }
        
        .code-line {
            min-height: 1.5em;
        }
        
        /* 번역된 주석 스타일 */
        .translated-comment {
            color: var(--comment-color);
            cursor: pointer;
            position: relative;
            background: rgba(106, 153, 85, 0.1);
            padding: 2px 4px;
            border-radius: 3px;
            transition: background 0.2s;
        }
        .translated-comment:hover {
            background: rgba(106, 153, 85, 0.3);
        }
        
        /* 툴팁 */
        .translated-comment .tooltip {
            display: none;
            position: absolute;
            bottom: 100%;
            left: 0;
            background: #333;
            color: #fff;
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 0.9em;
            white-space: pre-wrap;
            max-width: 600px;
            min-width: 200px;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            margin-bottom: 8px;
        }
        .translated-comment:hover .tooltip {
            display: block;
        }
        .tooltip-label {
            font-size: 0.75em;
            color: #aaa;
            margin-bottom: 5px;
            display: block;
        }
        
        /* 원문 보기 모드 */
        .show-original .translated-comment .trans-text { display: none; }
        .show-original .translated-comment .orig-text { display: inline; }
        .translated-comment .orig-text { display: none; }
        
        /* 기타 구문 */
        .code-keyword { color: var(--keyword-color); }
        .code-string { color: var(--string-color); }
        .code-function { color: var(--function-color); }
    </style>
</head>
<body>
    <div class="controls">
        <div class="file-info">
            <span class="filename">📄 ''' + html.escape(file_name) + '''</span>
            <span>''' + html.escape(file_type) + '''</span>
        </div>
        <div class="btn-group">
            <button class="btn" onclick="toggleTheme()">🌓 테마</button>
            <button class="btn" id="btn-mode" onclick="toggleMode()">📝 원문 보기</button>
        </div>
    </div>
    <div class="code-container">
        <div class="code-view" id="code-view">
'''
    
    code_html_footer = '''
        </div>
    </div>
    <script>
        function toggleTheme() {
            const body = document.body;
            const current = body.getAttribute('data-theme');
            body.setAttribute('data-theme', current === 'light' ? 'dark' : 'light');
        }
        function toggleMode() {
            const view = document.getElementById('code-view');
            const btn = document.getElementById('btn-mode');
            if (view.classList.contains('show-original')) {
                view.classList.remove('show-original');
                btn.textContent = '📝 원문 보기';
            } else {
                view.classList.add('show-original');
                btn.textContent = '🌐 번역 보기';
            }
        }
    </script>
</body>
</html>
'''
    
    # 원본 코드에서 주석을 직접 찾아서 대체
    # 위치 기반 대체 대신 텍스트 기반 대체 사용 (더 안정적)
    new_content = html.escape(original_content)
    
    # 번역 맵을 길이순으로 정렬 (긴 것 먼저 대체해서 부분 매칭 방지)
    sorted_translations = sorted(
        [(orig, trans) for orig, trans in translation_map.items() if orig != trans],
        key=lambda x: len(x[0]),
        reverse=True
    )
    
    for original_text, translated_text in sorted_translations:
        if original_text.strip():
            # HTML 이스케이프된 원본 텍스트 찾기
            escaped_orig = html.escape(original_text)
            
            if escaped_orig in new_content:
                # 툴팁용 원문
                safe_orig_tooltip = escaped_orig.replace('\n', '&#10;')
                safe_trans = html.escape(translated_text)
                
                replacement = f'<span class="translated-comment"><span class="trans-text">{safe_trans}</span><span class="orig-text">{escaped_orig}</span><span class="tooltip"><span class="tooltip-label">원문:</span>{safe_orig_tooltip}</span></span>'
                
                # 첫 번째 매치만 대체 (같은 주석이 여러 번 나올 수 있으므로)
                new_content = new_content.replace(escaped_orig, replacement, 1)
    
    # 줄 번호와 함께 HTML 생성
    lines = new_content.split('\n')
    line_nums_html = '<div class="line-numbers">'
    code_html = '<div class="code-content">'
    
    for i, line in enumerate(lines, 1):
        line_nums_html += f'{i}<br>'
        # 빈 줄 처리
        if not line.strip() and '<span' not in line:
            code_html += '<div class="code-line">&nbsp;</div>'
        else:
            code_html += f'<div class="code-line">{line}</div>'
    
    line_nums_html += '</div>'
    code_html += '</div>'
    
    if progress_cb:
        progress_cb(1.0, "HTML 생성 완료")
    
    return code_html_header + line_nums_html + code_html + code_html_footer


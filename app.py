"""
app.py
======
Docling PDF 번역기의 웹 인터페이스(Streamlit) 진입점입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **UI 구성**: Streamlit을 사용하여 사이드바(설정)와 메인 영역(파일 업로드, 결과 표시)을 구성합니다.
2.  **상태 관리**: 세션 상태(Session State)를 사용하여 번역 기록, 언어 설정 등을 관리합니다.
3.  **문서 처리 요청**: `src.core.process_document`를 호출하여 문서 변환 및 번역을 실행합니다.
4.  **결과 표시**: 번역된 결과를 화면에 보여주고, 다운로드 기능을 제공합니다.
5.  **히스토리 관리**: `src.utils.load_history_from_disk`를 통해 이전 작업 기록을 불러옵니다.
"""

import streamlit as st
import os
import logging
from pathlib import Path
import shutil

# src 모듈 임포트
from src.core import process_document, create_converter
from src.i18n import t, set_current_lang, get_current_lang
from src.utils import create_zip, inject_images, load_history_from_disk

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# Streamlit 페이지 설정 (반드시 가장 먼저 호출)
st.set_page_config(
    page_title="Docling PDF Translator",
    page_icon="🌐",
    layout="wide"
)

# 캐시된 Converter 생성 (리소스 재사용)
@st.cache_resource
def get_converter():
    """
    Docling Converter 인스턴스를 캐싱하여 반환합니다.
    앱 실행 중 한 번만 생성되어 재사용됩니다.
    """
    return create_converter()

def main():
    """
    메인 앱 실행 함수입니다.
    """
    # 1. 세션 상태 초기화
    if "history" not in st.session_state:
        # 앱 시작 시 디스크에서 히스토리 로드
        st.session_state.history = load_history_from_disk()

    # 언어 변경 콜백
    def set_lang_and_rerun():
        st.session_state["lang"] = st.session_state["lang_choice"]
        # st.rerun()은 segmented_control/radio의 on_change에서 자동 처리됨

    # 2. 사이드바: 설정 영역
    with st.sidebar:
        st.header(t("sidebar_header"))
        
        # 언어 선택 UI (Streamlit 버전에 따라 분기)
        lang_options = ["ko", "en"]
        if hasattr(st, "segmented_control"):
            st.segmented_control(
                t("language_label"),
                options=lang_options,
                format_func=lambda x: t(f"lang_option_{x}"),
                selection_mode="single",
                default=get_current_lang(),
                key="lang_choice",
                on_change=set_lang_and_rerun
            )
        else:
            st.radio(
                t("language_label"),
                options=lang_options,
                format_func=lambda x: t(f"lang_option_{x}"),
                index=0 if get_current_lang() == "ko" else 1,
                horizontal=True,
                key="lang_choice",
                on_change=set_lang_and_rerun
            )

        st.markdown("---")
        
        # 번역 옵션
        st.subheader(t("options_label"))
        
        source_lang = st.selectbox(t("src_label"), ["en", "fr", "de", "es", "it", "ja", "zh", "ko"], index=0)
        target_lang = st.selectbox(t("dest_label"), ["ko", "en", "fr", "de", "es", "it", "ja", "zh"], index=0)
        
        engine = st.selectbox(t("engine_label"), ["google", "deepl", "gemini", "openai", "qwen-0.6b", "yanolja"], index=0)
        
        default_workers = 1 if engine in ["qwen-0.6b", "yanolja"] else 8
        max_workers = st.number_input(
            t("workers_label"), 
            min_value=1, 
            max_value=16, 
            value=default_workers,
            help=t("workers_help")
        )

    # 3. 메인 영역: 타이틀 및 파일 업로드
    st.title(t("app_title"))

    # CSS Hack: 파일 업로더 텍스트 커스터마이징
    # Streamlit 기본 업로더 텍스트를 숨기고, 선택된 언어에 맞는 텍스트를 표시합니다.
    st.markdown(f"""
    <style>
        /* Hide the default text */
        [data-testid="stFileUploader"] section > div > div > span {{
            display: none;
        }}
        /* Insert custom text */
        [data-testid="stFileUploader"] section > div > div::after {{
            content: "{t('uploader_text')}";
            display: block;
            text-align: center;
            margin-top: 10px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        t("upload_label"),
        type=["pdf", "docx", "pptx", "html", "htm", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help=t("uploader_limit")
    )

    # 4. 번역 실행
    if uploaded_files:
        if st.button(t("translate_button"), type="primary"):
            converter = get_converter()
            
            # 진행 상태 표시줄
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_files = len(uploaded_files)
            results = []

            for i, uploaded_file in enumerate(uploaded_files):
                # 임시 파일 저장
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # 진행률 콜백
                def update_progress(ratio, msg):
                    # 전체 진행률 = (현재 파일 인덱스 + 현재 파일 진행률) / 전체 파일 수
                    global_ratio = (i + ratio) / total_files
                    progress_bar.progress(min(global_ratio, 1.0))
                    status_text.text(t("status_processing").format(
                        current=i+1, total=total_files, filename=uploaded_file.name
                    ) + f" ({msg})")

                try:
                    # 핵심 처리 로직 호출
                    result = process_document(
                        file_path=uploaded_file.name,
                        converter=converter,
                        source_lang=source_lang,
                        dest_lang=target_lang,
                        engine=engine,
                        max_workers=max_workers,
                        progress_cb=update_progress
                    )
                    
                    if result:
                        results.append({
                            "filename": uploaded_file.name,
                            "output_dir": str(result["output_dir"]),
                            "html_path": str(result["html_path"])
                        })
                    
                    # 임시 파일 삭제
                    os.remove(uploaded_file.name)

                except Exception as e:
                    st.error(t("translate_error").format(filename=uploaded_file.name, error=str(e)))
                    logging.error(f"Processing failed for {uploaded_file.name}: {e}")

            progress_bar.progress(1.0)
            status_text.text(t("status_all_done"))
            
            # 히스토리에 결과 추가 및 저장
            if results:
                timestamp = results[0]["output_dir"].split("_")[-2] + "_" + results[0]["output_dir"].split("_")[-1] # 폴더명에서 추출
                
                # 타임스탬프 포맷팅
                from datetime import datetime
                try:
                    dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                    display_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    display_time = timestamp

                new_history_item = {
                    "timestamp": display_time,
                    "results": results,
                    "source": source_lang,
                    "target": target_lang,
                    "engine": engine
                }
                st.session_state.history.insert(0, new_history_item)
                st.success(t("batch_success").format(n=len(results)))
                st.info(t("batch_hint"))

    st.markdown("---")

    # 5. 히스토리 및 결과 표시 영역
    if st.session_state.history:
        st.header(t("history_header"))
        
        # 히스토리 선택 옵션 포맷팅
        def format_history_option(h):
            files = [r['filename'] for r in h['results']]
            if len(files) == 1:
                file_str = files[0]
            else:
                file_str = f"{files[0]} + {len(files)-1} others"
            return f"[{h['timestamp']}] {file_str} ({h['source']}->{h['target']})"

        history_options = [format_history_option(h) for h in st.session_state.history]
        
        selected_idx = st.selectbox(
            t("history_select_label"),
            range(len(history_options)),
            format_func=lambda i: history_options[i],
            placeholder=t("history_placeholder")
        )
        
        if selected_idx is not None:
            selected_record = st.session_state.history[selected_idx]
            
            st.subheader(t("batch_result_header").format(n=len(selected_record['results'])))
            
            # 상단 컨트롤 영역 (집중 모드, 검수 모드)
            # 컬럼 비율 조정하여 토글 버튼들이 한 줄에 잘 나오도록 함
            c_head, c_blank, c_view, c_focus = st.columns([6, 2, 2, 2])
            with c_view:
                # 검수 모드 (기본값: True -> 좌우 대조)
                view_mode = st.toggle(t("view_mode_label"), value=True, key="view_mode", help=t("view_mode_help"))
            with c_focus:
                # 집중 모드
                focus_mode = st.toggle(t("focus_mode_label"), key="focus_mode", help=t("focus_mode_help"))
            
            # 각 결과 파일별 탭 생성
            tabs = st.tabs([res['filename'] for res in selected_record['results']])
            
            for i, res in enumerate(selected_record['results']):
                with tabs[i]:
                    output_dir = Path(res['output_dir'])
                    html_path = Path(res['html_path'])
                    
                    if not html_path.exists():
                        st.error(t("html_not_found"))
                        continue

                    # HTML 읽기 및 이미지 임베딩
                    with open(html_path, "r", encoding="utf-8") as f:
                        html_content = f.read()
                    
                    # 로컬 이미지를 Base64로 변환하여 HTML에 주입
                    html_content = inject_images(html_content, output_dir)

                    # 뷰 모드 설정 스크립트 주입
                    # HTML 로드 직후 실행되도록 body 끝에 스크립트 추가
                    if view_mode:
                        # 검수 모드 활성화 (view-mode-inspect 클래스 추가)
                        script = """
                        <script>
                            document.addEventListener('DOMContentLoaded', function() {
                                document.getElementById('content-container').classList.add('view-mode-inspect');
                                document.getElementById('btn-mode').classList.add('active');
                                document.getElementById('btn-mode').innerText = UI_STRINGS[currentUiLang].mode_read; // 버튼 텍스트는 반대로 (누르면 읽기모드)
                                updateUiText();
                            });
                        </script>
                        """
                        html_content += script
                    else:
                        # 읽기 모드 (기본값이지만 명시적으로 제거 보장)
                        script = """
                        <script>
                            document.addEventListener('DOMContentLoaded', function() {
                                document.getElementById('content-container').classList.remove('view-mode-inspect');
                                document.getElementById('btn-mode').classList.remove('active');
                                updateUiText();
                            });
                        </script>
                        """
                        html_content += script

                    if focus_mode:
                        # 집중 모드: 1컬럼 (전체 너비) + 다운로드 옵션은 Expander로 이동
                        st.info(t("single_tip"))
                        
                        # 뷰어 (전체 너비)
                        st.components.v1.html(html_content, height=900, scrolling=True)
                        
                        # 다운로드 옵션 (Expander)
                        with st.expander(t("download_options_label"), expanded=False):
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                zip_path = create_zip(output_dir)
                                with open(zip_path, "rb") as f:
                                    st.download_button(
                                        label=t("zip_download"),
                                        data=f,
                                        file_name=f"{res['filename']}_translated.zip",
                                        mime="application/zip",
                                        key=f"zip_{selected_idx}_{i}_focus"
                                    )
                            with c2:
                                st.download_button(
                                    label=t("html_download_interactive"),
                                    data=html_content,
                                    file_name=f"{res['filename']}_interactive.html",
                                    mime="text/html",
                                    key=f"html_{selected_idx}_{i}_focus"
                                )
                            with c3:
                                if st.button(t("open_folder"), key=f"open_{selected_idx}_{i}_focus"):
                                    try:
                                        os.startfile(output_dir)
                                        st.success(t("open_folder_success").format(path=output_dir))
                                    except Exception as e:
                                        st.error(t("open_folder_failed").format(error=e))

                    else:
                        # 기본 모드: 2컬럼 레이아웃 (3:1)
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.info(t("single_tip"))
                            # iframe으로 HTML 표시
                            st.components.v1.html(html_content, height=800, scrolling=True)

                        with col2:
                            st.write(f"**{t('single_result_header').format(name=res['filename'])}**")
                            
                            # ZIP 다운로드 버튼
                            zip_path = create_zip(output_dir)
                            with open(zip_path, "rb") as f:
                                st.download_button(
                                    label=t("zip_download"),
                                    data=f,
                                    file_name=f"{res['filename']}_translated.zip",
                                    mime="application/zip",
                                    key=f"zip_{selected_idx}_{i}"
                                )
                            
                            # HTML 다운로드 버튼
                            st.download_button(
                                label=t("html_download_interactive"),
                                data=html_content,
                                file_name=f"{res['filename']}_interactive.html",
                                mime="text/html",
                                key=f"html_{selected_idx}_{i}"
                            )
                            
                            # 폴더 열기 (로컬 환경 전용)
                            if st.button(t("open_folder"), key=f"open_{selected_idx}_{i}"):
                                try:
                                    os.startfile(output_dir)
                                    st.success(t("open_folder_success").format(path=output_dir))
                                except Exception as e:
                                    st.error(t("open_folder_failed").format(error=e))

if __name__ == "__main__":
    main()

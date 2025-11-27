import streamlit as st
import os
import tempfile
import shutil
import zipfile
from pathlib import Path
import streamlit.components.v1 as components
from main import process_document

# Docling 관련 임포트
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
    PowerpointFormatOption,
    HTMLFormatOption,
    ImageFormatOption,
)
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

# ==== i18n: 화면에 보이는 문자열 번역 딕셔너리 및 헬퍼 ====
TRANSLATIONS = {
    "en": {
        # 언어 선택 라벨
        "lang_option_ko": "Korean",
        "lang_option_en": "English",

        # 업로더 텍스트 (CSS Hack용)
        "uploader_text": "Drag and drop files here",
        "uploader_limit": "Limit 50GB per file • PDF, DOCX, PPTX, HTML, HTM, PNG, JPG, JPEG",

        # 타이틀 / 사이드바
        "app_title": "Docling PDF Translator",
        "sidebar_header": "Settings",
        "upload_label": "Upload documents (PDF, DOCX, PPTX, HTML, Image, etc.)",
        "options_label": "Translation options",
        "src_label": "Source language",
        "dest_label": "Target language",
        "engine_label": "Translation engine",
        "workers_label": "Number of parallel workers",
        "workers_help": "Higher means faster but uses more system resources. Recommended: 8",
        "translate_button": "Start new translation",
        "history_header": "Translation history",
        "history_select_label": "Select previous result",
        "history_placeholder": "Select a record...",

        # 진행 상태 / 배치 결과
        "status_processing": "[{current}/{total}] Processing: {filename}...",
        "status_all_done": "All tasks have been completed!",
        "batch_success": "Successfully translated {n} file(s)!",
        "batch_hint": "👇 You can check the results for each file below.",
        "batch_result_header": "📦 Batch translation results ({n} file(s))",

        # 번역 중 에러
        "translate_error": "An error occurred while processing {filename}: {error}",

        # 히스토리 관련
        "history_missing_files": "Could not find result files in the selected record.",
        "history_load_failed": "Failed to load history: {error}",

        # 탭 / 공통 다운로드 설명
        "tab_interactive": "Interactive view",
        "tab_download": "Download",
        "download_desc": "You can download the translated results or open the folder.",

        # HTML / 폴더 관련
        "html_not_found": "Could not find the HTML file.",
        "open_folder": "📂 Open result folder",
        "open_folder_primary": "📂 Open result folder",
        "open_folder_failed": "Failed to open the folder: {error}",
        "open_folder_success": "Opened folder: {path}",


        # 단일 결과 영역
        "single_result_header": "Result: {name}",
        "single_tip": "💡 Tip: Use the buttons at the top right of the result page to switch view modes (side-by-side / expanded).",

        # 다운로드 버튼 라벨
        "zip_download": "📦 Download ZIP",
        "html_download": "🌐 Download HTML",
        "zip_download_all": "📦 Download all results (ZIP)",
        "html_download_interactive": "🌐 Download interactive HTML",
    },
    "ko": {
        # 언어 선택 라벨
        "lang_option_ko": "한국어",
        "lang_option_en": "영어",

        # 업로더 텍스트 (CSS Hack용)
        "uploader_text": "파일을 이곳에 드래그 앤 드롭하세요",
        "uploader_limit": "파일당 50GB 제한 • PDF, DOCX, PPTX, HTML, HTM, PNG, JPG, JPEG",

        # 타이틀 / 사이드바
        "app_title": "Docling PDF 번역기",
        "sidebar_header": "설정",
        "upload_label": "문서 업로드 (PDF, DOCX, PPTX, HTML, Image 등)",
        "options_label": "번역 옵션",
        "src_label": "원본 언어 (Source)",
        "dest_label": "대상 언어 (Target)",
        "engine_label": "번역 엔진",
        "workers_label": "병렬 처리 워커 수 (Workers)",
        "workers_help": "높을수록 빠르지만 시스템 리소스를 많이 사용합니다. 권장: 8",
        "translate_button": "새로 번역 시작",
        "history_header": "번역 기록",
        "history_select_label": "이전 번역 결과 선택",
        "history_placeholder": "기록을 선택하세요...",

        # 진행 상태 / 배치 결과
        "status_processing": "[{current}/{total}] 처리 중: {filename}...",
        "status_all_done": "모든 작업이 완료되었습니다!",
        "batch_success": "총 {n}개의 파일 번역이 완료되었습니다!",
        "batch_hint": "👇 아래에서 각 파일의 결과를 확인할 수 있습니다.",
        "batch_result_header": "📦 배치 번역 결과 ({n}개 파일)",

        # 번역 중 에러
        "translate_error": "오류가 발생했습니다 ({filename}): {error}",

        # 히스토리 관련
        "history_missing_files": "선택한 기록에서 결과 파일을 찾을 수 없습니다.",
        "history_load_failed": "기록 불러오기 실패: {error}",

        # 탭 / 공통 다운로드 설명
        "tab_interactive": "인터랙티브 뷰",
        "tab_download": "다운로드",
        "download_desc": "번역된 결과물들을 다운로드하거나 폴더를 열어 확인할 수 있습니다.",

        # HTML / 폴더 관련
        "html_not_found": "HTML 파일을 찾을 수 없습니다.",
        "open_folder": "📂 결과 폴더 열기",
        "open_folder_primary": "📂 결과 폴더 열기",
        "open_folder_failed": "폴더를 열 수 없습니다: {error}",
        "open_folder_success": "폴더를 열었습니다: {path}",


        # 단일 결과 영역
        "single_result_header": "결과: {name}",
        "single_tip": "💡 **팁:** 결과물 페이지 우측 상단의 버튼을 눌러 뷰 모드(좌우 병렬 / 펼치기)를 변경할 수 있습니다.",

        # 다운로드 버튼 라벨
        "zip_download": "📦 ZIP 다운로드",
        "html_download": "🌐 HTML 다운로드",
        "zip_download_all": "📦 전체 결과 다운로드 (ZIP)",
        "html_download_interactive": "🌐 인터랙티브 HTML 다운로드",
    },
}


def get_current_lang() -> str:
    """현재 UI 언어 코드(en/ko)를 세션에서 가져옵니다. 기본값은 'ko'."""
    if "lang" not in st.session_state:
        st.session_state["lang"] = "ko"  # 기본: 한국어
    return st.session_state["lang"]


def set_current_lang(lang_code: str) -> None:
    """현재 UI 언어 코드를 세션에 저장합니다."""
    st.session_state["lang"] = lang_code


def t(key: str) -> str:
    """현재 언어에 맞는 문자열을 TRANSLATIONS에서 가져옵니다. 없으면 영어 → 키 순으로 fallback."""
    lang = get_current_lang()
    return TRANSLATIONS.get(lang, {}).get(
        key,
        TRANSLATIONS.get("en", {}).get(key, key),
    )


# 페이지 설정 (여기 제목은 브라우저 탭용이라 그대로 둠)
st.set_page_config(
    page_title="Docling Translate Web Viewer",
    page_icon="📄",
    layout="wide",
)

OUTPUT_DIR = Path("output")


def get_history():
    """output 폴더 아래의 번역 결과 디렉토리들을 최신순으로 가져옵니다."""
    if not OUTPUT_DIR.exists():
        return []
    dirs = [d for d in OUTPUT_DIR.iterdir() if d.is_dir()]
    dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return dirs


def create_zip(folder_path: Path) -> Path:
    """주어진 폴더 전체를 ZIP으로 압축하고 그 경로를 반환합니다."""
    zip_path = folder_path / "result.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file == "result.zip":
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    return zip_path


import re
import base64


def inject_images(html_content: str, folder_path: Path) -> str:
    """
    HTML 내용 중 로컬 이미지 경로(images/...)를 찾아 Base64로 임베딩합니다.
    Streamlit의 iframe 보안 정책상 로컬 파일을 직접 로드할 수 없기 때문입니다.
    """

    def replace_match(match: re.Match) -> str:
        img_rel_path = match.group(1)  # 예: images/filename.png
        img_full_path = folder_path / img_rel_path

        if img_full_path.exists():
            try:
                with open(img_full_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode("utf-8")
                ext = img_full_path.suffix.lower().replace(".", "")
                return f'src="data:image/{ext};base64,{img_b64}"'
            except Exception as e:
                print(f"이미지 임베딩 실패: {e}")
                return match.group(0)
        return match.group(0)

    # main.py에서 생성하는 패턴: src="images/filename.png"
    pattern = r'src="(images/[^"]+)"'
    return re.sub(pattern, replace_match, html_content)


def main():
    # 상단: 타이틀 + 언어 선택 (우측 정렬)
    col_title, col_lang = st.columns([5, 1])

    with col_title:
        st.title(f"📄 {t('app_title')}")

    with col_lang:
        st.write("") # Vertical spacer to align with title
        current_lang = get_current_lang()
        # 토글 버튼: 현재 언어의 반대 언어를 라벨로 표시
        next_lang = "en" if current_lang == "ko" else "ko"
        btn_label = "English" if current_lang == "ko" else "한국어"

        if st.button(btn_label, key="lang_toggle"):
            set_current_lang(next_lang)
            st.rerun()

    # CSS Hack: 파일 업로더 텍스트 번역 (수정됨: 레이아웃 깨짐 방지)
    # font-size: 0 기법을 사용하여 원본 텍스트만 숨기고 레이아웃은 유지
    uploader_css = f"""
    <style>
    /* 1. 메인 텍스트 (Drag and drop files here) */
    [data-testid="stFileUploaderDropzoneInstructions"] > div:first-child {{
        font-size: 0;
    }}
    [data-testid="stFileUploaderDropzoneInstructions"] > div:first-child::after {{
        content: "{t('uploader_text')}";
        font-size: 1rem;
        font-weight: bold;
        display: block;
    }}
    
    /* 2. 서브 텍스트 (Limit 200MB...) */
    [data-testid="stFileUploaderDropzoneInstructions"] small {{
        font-size: 0;
        display: block;
    }}
    [data-testid="stFileUploaderDropzoneInstructions"] small::after {{
        content: "{t('uploader_limit')}";
        font-size: 0.85rem;
        display: block;
    }}
    </style>
    """
    st.markdown(uploader_css, unsafe_allow_html=True)

    # Docling DocumentConverter 초기화 (한 번만 설정)
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.generate_picture_images = True
    pipeline_options.generate_table_images = True
    pipeline_options.images_scale = 2.0

    global_converter = DocumentConverter(
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

    # 사이드바: 설정 + 히스토리
    with st.sidebar:
        st.header(t("sidebar_header"))

        # 1. 파일 업로드
        uploaded_files = st.file_uploader(
            t("upload_label"),
            type=["pdf", "docx", "pptx", "html", "htm", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
        )

        # 2. 언어 및 엔진 설정
        with st.expander(t("options_label"), expanded=True):
            src_lang = st.selectbox(
                t("src_label"),
                ["auto", "en", "ko", "ja", "zh"],
                index=1,
            )
            dest_lang = st.selectbox(
                t("dest_label"),
                ["en", "ko", "ja", "zh"],
                index=1,
            )
            engine = st.selectbox(
                t("engine_label"),
                ["google", "deepl", "gemini", "openai"],
                index=0,
            )
            max_workers = st.number_input(
                t("workers_label"),
                min_value=1,
                max_value=16,
                value=8,
                step=1,
                help=t("workers_help"),
            )

        translate_btn = st.button(
            t("translate_button"),
            type="primary",
            disabled=not uploaded_files,
        )

        st.divider()

        # 3. 번역 히스토리
        st.subheader(t("history_header"))
        history_dirs = get_history()
        selected_history = st.selectbox(
            t("history_select_label"),
            options=history_dirs,
            format_func=lambda x: x.name,
            index=None,
            placeholder=t("history_placeholder"),
        )

    # 세션 상태 초기화
    if "current_result" not in st.session_state:
        st.session_state.current_result = None

    # 새로 번역 실행
    if translate_btn and uploaded_files:
        progress_bar = st.progress(0)
        status_text = st.empty()

        total_files = len(uploaded_files)
        all_results = []    # 모든 결과를 저장

        for i, uploaded_file in enumerate(uploaded_files):
            # 진행 상태 표시
            status_text.text(
                t("status_processing").format(
                    current=i + 1,
                    total=total_files,
                    filename=uploaded_file.name,
                )
            )

            tmp_path = None
            try:
                # 업로드된 파일을 임시 파일로 저장
                suffix = Path(uploaded_file.name).suffix
                if not suffix:
                    suffix = ".pdf" #Fallback

                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=suffix
                ) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                # main.py의 process_document 호출
                result_paths = process_document(
                    tmp_path,
                    global_converter, # converter 인자 추가
                    src_lang,
                    dest_lang,
                    engine,
                    max_workers,
                )
                all_results.append(result_paths)

            except Exception as e:
                # 파일별 에러 표시
                st.error(
                    t("translate_error").format(
                        filename=uploaded_file.name,
                        error=str(e),
                    )
                )
            finally:
                # 임시 파일 정리
                if tmp_path and os.path.exists(tmp_path):
                    os.unlink(tmp_path)

            # 진행률 업데이트
            progress_bar.progress((i + 1) / total_files)

        # 전체 작업 완료 메시지
        status_text.text(t("status_all_done"))

        # 배치 결과를 세션에 저장
        st.session_state.batch_results = all_results
        st.session_state.current_result = None

        st.success(
            t("batch_success").format(n=len(all_results))
        )
        st.info(t("batch_hint"))

    # 히스토리에서 결과 선택
    elif selected_history:
        # 히스토리 폴더에서 파일 경로 추론
        folder = selected_history
        # 파일명 규칙: 폴더명에서 타임스탬프 등을 제외하고 추론하거나, glob으로 찾음
        # 여기서는 간단히 glob으로 주요 파일 찾기
        try:
            html_files = list(folder.glob("*_interactive.html"))
            combined_md_files = list(folder.glob("*_combined.md"))

            if html_files and combined_md_files:
                st.session_state.current_result = {
                    "output_dir": folder,
                    "html_path": html_files[0],
                    "combined_md": combined_md_files[0],
                }
            else:
                st.warning(t("history_missing_files"))
        except Exception as e:
            st.error(
                t("history_load_failed").format(error=str(e))
            )

    # 배치(여러 파일) 결과 표시
    if "batch_results" in st.session_state and st.session_state.batch_results:
        st.divider()
        st.subheader(
            t("batch_result_header").format(
                n=len(st.session_state.batch_results)
            )
        )

        tab_labels = [res["output_dir"].name for res in st.session_state.batch_results]
        tabs = st.tabs(tab_labels)

        for idx, (tab, res) in enumerate(zip(tabs, st.session_state.batch_results)):
            with tab:
                output_dir = res["output_dir"]
                html_path = res["html_path"]

                # 서브탭: 인터랙티브 뷰 / 다운로드
                subtab1, subtab2 = st.tabs(
                    [t("tab_interactive"), t("tab_download")]
                )

                with subtab1:
                    if html_path.exists():
                        with open(html_path, "r", encoding="utf-8") as f:
                            html_content = f.read()
                        html_content_view = inject_images(html_content, output_dir)
                        components.html(
                            html_content_view,
                            height=600,
                            scrolling=True,
                        )
                    else:
                        st.error(t("html_not_found"))

                with subtab2:
                    st.info(t("download_desc"))

                    if st.button(
                        t("open_folder"),
                        key=f"open_{idx}",
                    ):
                        try:
                            os.startfile(output_dir)
                            st.success(
                                t("open_folder_success").format(path=str(output_dir))
                            )
                        except Exception as e:
                            st.error(
                                t("open_folder_failed").format(error=str(e))
                            )

                    st.divider()

                    col1, col2 = st.columns(2)
                    with col1:
                        zip_path = create_zip(output_dir)
                        with open(zip_path, "rb") as f:
                            zip_data = f.read()
                        st.download_button(
                            label=t("zip_download"),
                            data=zip_data,
                            file_name=f"{output_dir.name}.zip",
                            mime="application/zip",
                            key=f"zip_{idx}",
                        )

                    with col2:
                        if html_path.exists():
                            with open(html_path, "rb") as f:
                                html_data = f.read()
                            st.download_button(
                                label=t("html_download"),
                                data=html_data,
                                file_name=html_path.name,
                                mime="text/html",
                                key=f"html_{idx}",
                            )

    # 단일 결과(히스토리에서 선택한 경우) 표시
    elif st.session_state.current_result:
        res = st.session_state.current_result
        output_dir = res["output_dir"]
        html_path = res["html_path"]

        st.divider()
        st.subheader(
            t("single_result_header").format(name=output_dir.name)
        )

        tab1, tab2 = st.tabs(
            [t("tab_interactive"), t("tab_download")]
        )

        with tab1:
            st.info(t("single_tip"))
            if html_path.exists():
                with open(html_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                html_content_view = inject_images(html_content, output_dir)
                components.html(
                    html_content_view,
                    height=800,
                    scrolling=True,
                )
            else:
                st.error(t("html_not_found"))

        with tab2:
            st.info(t("download_desc"))

            if st.button(
                t("open_folder_primary"),
                type="primary",
            ):
                try:
                    os.startfile(output_dir)
                    st.success(
                        t("open_folder_success").format(path=str(output_dir))
                    )
                except Exception as e:
                    st.error(
                        t("open_folder_failed").format(error=str(e))
                    )

            st.divider()

            col_dl1, col_dl2 = st.columns(2)

            with col_dl1:
                zip_path = create_zip(output_dir)
                with open(zip_path, "rb") as f:
                    zip_data = f.read()
                st.download_button(
                    label=t("zip_download_all"),
                    data=zip_data,
                    file_name=f"{output_dir.name}.zip",
                    mime="application/zip",
                )

            with col_dl2:
                if html_path.exists():
                    with open(html_path, "rb") as f:
                        html_data = f.read()
                    st.download_button(
                        label=t("html_download_interactive"),
                        data=html_data,
                        file_name=html_path.name,
                        mime="text/html",
                    )


if __name__ == "__main__":
    main()

import streamlit as st
import os
import tempfile
import shutil
import zipfile
from pathlib import Path
import streamlit.components.v1 as components
from main import process_document

# 페이지 설정
st.set_page_config(
    page_title="Docling Translate Web Viewer",
    page_icon="📄",
    layout="wide"
)

OUTPUT_DIR = Path("output")

def get_history():
    """output 폴더에서 번역 히스토리를 가져옵니다."""
    if not OUTPUT_DIR.exists():
        return []
    # 디렉토리만 필터링하고 최신순으로 정렬
    dirs = [d for d in OUTPUT_DIR.iterdir() if d.is_dir()]
    dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return dirs

def create_zip(folder_path):
    """폴더 전체를 zip으로 압축합니다."""
    zip_path = folder_path / "result.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
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

def inject_images(html_content, folder_path):
    """
    HTML 내용 중 로컬 이미지 경로(images/...)를 찾아 Base64로 변환하여 임베딩합니다.
    Streamlit iframe 보안 정책상 로컬 파일을 직접 로드할 수 없기 때문입니다.
    """
    def replace_match(match):
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

    # src="images/..." 패턴을 찾아서 교체
    # main.py가 생성하는 패턴: src="images/filename.png"
    pattern = r'src="(images/[^"]+)"'
    return re.sub(pattern, replace_match, html_content)

def main():
    st.title("📄 Docling PDF Translator")
    
    # 사이드바: 히스토리 및 설정
    with st.sidebar:
        st.header("설정")
        
        # 1. 파일 업로드
        uploaded_files = st.file_uploader("PDF 파일 업로드 (여러 개 선택 가능)", type=["pdf"], accept_multiple_files=True)
        
        # 2. 언어 및 엔진 설정
        with st.expander("번역 옵션", expanded=True):
            src_lang = st.selectbox("원본 언어 (Source)", ["auto", "en", "ko", "ja", "zh"], index=1)
            dest_lang = st.selectbox("대상 언어 (Target)", ["en", "ko", "ja", "zh"], index=1)
            engine = st.selectbox("번역 엔진", ["google", "deepl", "gemini"], index=0)
            max_workers = st.number_input(
                "병렬 처리 워커 수 (Workers)", 
                min_value=1, 
                max_value=16, 
                value=8,
                step=1,
                help="높을수록 빠르지만 시스템 리소스를 많이 사용합니다. 권장: 8"
            )
        
        translate_btn = st.button("새로 번역 시작", type="primary", disabled=not uploaded_files)

        st.divider()
        
        # 3. 히스토리
        st.subheader("번역 기록")
        history_dirs = get_history()
        selected_history = st.selectbox(
            "이전 번역 결과 선택", 
            options=history_dirs, 
            format_func=lambda x: x.name,
            index=None,
            placeholder="기록을 선택하세요..."
        )

    # 상태 관리
    if "current_result" not in st.session_state:
        st.session_state.current_result = None

    # 번역 로직
    if translate_btn and uploaded_files:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_files = len(uploaded_files)
        all_results = []  # 모든 결과를 저장
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"[{i+1}/{total_files}] 처리 중: {uploaded_file.name}...")
            
            try:
                # 임시 파일로 저장
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                # main.py의 process_document 호출
                result_paths = process_document(tmp_path, src_lang, dest_lang, engine, max_workers)
                all_results.append(result_paths)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다 ({uploaded_file.name}): {str(e)}")
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            
            # 진행률 업데이트
            progress_bar.progress((i + 1) / total_files)
            
        status_text.text("모든 작업이 완료되었습니다!")
        
        # 모든 결과를 세션 상태에 저장
        st.session_state.batch_results = all_results
        st.session_state.current_result = None  # 단일 결과는 초기화
        
        st.success(f"총 {len(all_results)}개의 파일 번역이 완료되었습니다!")
        st.info("👇 아래에서 각 파일의 결과를 확인할 수 있습니다.")

    
    # 히스토리 선택 로직
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
                    "combined_md": combined_md_files[0]
                }
            else:
                st.warning("선택한 기록에서 결과 파일을 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"기록 불러오기 실패: {e}")

    # 배치 결과 표시 (여러 파일)
    if "batch_results" in st.session_state and st.session_state.batch_results:
        st.divider()
        st.subheader(f"📦 배치 번역 결과 ({len(st.session_state.batch_results)}개 파일)")
        
        # 각 파일별로 탭 생성
        tab_labels = [res["output_dir"].name for res in st.session_state.batch_results]
        tabs = st.tabs(tab_labels)
        
        for idx, (tab, res) in enumerate(zip(tabs, st.session_state.batch_results)):
            with tab:
                output_dir = res["output_dir"]
                html_path = res["html_path"]
                
                # 서브탭: 인터랙티브 뷰 / 다운로드
                subtab1, subtab2 = st.tabs(["인터랙티브 뷰", "다운로드"])
                
                with subtab1:
                    if html_path.exists():
                        with open(html_path, "r", encoding="utf-8") as f:
                            html_content = f.read()
                        html_content_view = inject_images(html_content, output_dir)
                        components.html(html_content_view, height=600, scrolling=True)
                    else:
                        st.error("HTML 파일을 찾을 수 없습니다.")
                
                with subtab2:
                    st.info("번역된 결과물들을 다운로드하거나 폴더를 열어 확인할 수 있습니다.")
                    
                    if st.button(f"📂 결과 폴더 열기", key=f"open_{idx}"):
                        try:
                            os.startfile(output_dir)
                            st.success(f"폴더를 열었습니다: {output_dir}")
                        except Exception as e:
                            st.error(f"폴더를 열 수 없습니다: {e}")
                    
                    st.divider()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        zip_path = create_zip(output_dir)
                        with open(zip_path, "rb") as f:
                            zip_data = f.read()
                        st.download_button(
                            label="📦 ZIP 다운로드",
                            data=zip_data,
                            file_name=f"{output_dir.name}.zip",
                            mime="application/zip",
                            key=f"zip_{idx}"
                        )
                    
                    with col2:
                        if html_path.exists():
                            with open(html_path, "rb") as f:
                                html_data = f.read()
                            st.download_button(
                                label="🌐 HTML 다운로드",
                                data=html_data,
                                file_name=html_path.name,
                                mime="text/html",
                                key=f"html_{idx}"
                            )
    
    # 단일 결과 표시 (히스토리 선택 시)
    elif st.session_state.current_result:
        res = st.session_state.current_result
        output_dir = res["output_dir"]
        html_path = res["html_path"]
        
        st.divider()
        st.subheader(f"결과: {output_dir.name}")

        # 탭 구성
        tab1, tab2 = st.tabs(["인터랙티브 뷰 (Interactive)", "다운로드 (Download)"])
        
                    with tab1:
                        st.info("💡 **팁:** 결과물 페이지 우측 상단의 버튼을 눌러 뷰 모드(좌우 병렬 / 펼치기)를 변경할 수 있습니다.")
                        # HTML 파일 읽어서 표시
                        if html_path.exists():
                            with open(html_path, "r", encoding="utf-8") as f:
                                html_content = f.read()
                            
                            # ⚠️ 웹 뷰어 표시용으로 이미지 경로를 Base64로 변환하여 주입
                            # 원본 파일은 건드리지 않음
                            html_content_view = inject_images(html_content, output_dir)
                            
                            # iframe으로 임베딩 (높이 조절 가능)
                            components.html(html_content_view, height=800, scrolling=True)            else:
                st.error("HTML 파일을 찾을 수 없습니다.")

        with tab2:
            st.info("번역된 결과물들을 다운로드하거나 폴더를 열어 확인할 수 있습니다.")
            
            # 로컬 폴더 열기 버튼 (Windows 전용)
            if st.button("📂 결과 폴더 열기 (Open Folder)", type="primary"):
                try:
                    os.startfile(output_dir)
                    st.success(f"폴더를 열었습니다: {output_dir}")
                except Exception as e:
                    st.error(f"폴더를 열 수 없습니다: {e}")
            
            st.divider()
            
            col_dl1, col_dl2 = st.columns(2)
            
            with col_dl1:
                # ZIP 생성 및 다운로드
                zip_path = create_zip(output_dir)
                with open(zip_path, "rb") as f:
                    zip_data = f.read()
                    
                st.download_button(
                    label="📦 전체 결과 다운로드 (ZIP)",
                    data=zip_data,
                    file_name=f"{output_dir.name}.zip",
                    mime="application/zip"
                )
            
            with col_dl2:
                # 개별 파일 다운로드 (HTML)
                if html_path.exists():
                    with open(html_path, "rb") as f:
                        html_data = f.read()
                        
                    st.download_button(
                        label="🌐 인터랙티브 HTML 다운로드",
                        data=html_data,
                        file_name=html_path.name,
                        mime="text/html"
                    )

if __name__ == "__main__":
    main()

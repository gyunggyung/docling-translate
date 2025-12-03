"""
src/utils.py
============
프로젝트 전반에서 사용되는 유틸리티 함수들을 모아둔 모듈입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **NLTK 리소스 관리**: 문장 분리에 필요한 NLTK 데이터를 확인하고 다운로드합니다.
2.  **파일 압축**: 결과 폴더를 ZIP 파일로 압축합니다.
3.  **이미지 주입**: 로컬 이미지를 Base64로 인코딩하여 HTML에 임베딩합니다 (웹 보안 문제 해결).
4.  **히스토리 로드**: `output/` 디렉토리를 스캔하여 이전 번역 기록을 불러옵니다.
"""

import re
import base64

import os
import nltk
import logging
from pathlib import Path
from pathlib import Path
from datetime import datetime
from typing import Union, Optional
from docling_core.types.doc import DoclingDocument, TableItem, PictureItem

def save_and_get_image_path(
    item: Union[TableItem, PictureItem],
    doc: DoclingDocument,
    output_dir: Path,
    base_filename: str,
    counters: dict
) -> Optional[str]:
    """
    Docling 아이템(표, 그림)을 이미지 파일로 저장하고 상대 경로를 반환합니다.
    
    Args:
        item: TableItem 또는 PictureItem
        doc: DoclingDocument 객체
        output_dir: 저장할 디렉토리 경로
        base_filename: 파일명 접두사
        counters: 이미지 번호 카운터 딕셔너리
        
    Returns:
        str: 저장된 이미지의 상대 경로 (예: "images/file_table_1.png") 또는 None
    """
    # 이미지 폴더 생성
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)
    
    # 타입 확인 및 이미지 데이터 가져오기
    image = None
    kind = ""
    
    if isinstance(item, TableItem):
        kind = "table"
        # TableItem은 get_image(doc) 메서드 사용
        if hasattr(item, "get_image"):
            image = item.get_image(doc)
    elif isinstance(item, PictureItem):
        kind = "picture"
        # PictureItem도 get_image(doc) 메서드 사용
        if hasattr(item, "get_image"):
            image = item.get_image(doc)
            
    if image:
        counters[kind] += 1
        count = counters[kind]
        filename = f"{base_filename}_{kind}_{count}.png"
        file_path = images_dir / filename
        
        try:
            image.save(file_path, "PNG")
            return f"images/{filename}"
        except Exception as e:
            logging.warning(f"이미지 저장 실패 ({filename}): {e}")
            return None
            
    return None

def ensure_nltk_resources():
    """
    문장 분리(Tokenization)에 필요한 NLTK 리소스를 확인하고, 없으면 다운로드합니다.
    'punkt', 'punkt_tab' 모델을 사용합니다.
    """
    try:
        nltk.data.find("tokenizers/punkt")
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        logging.info("NLTK 모델 다운로드 중...")
        nltk.download("punkt", quiet=True)
        nltk.download("punkt_tab", quiet=True)
        logging.info("NLTK 모델 다운로드 완료.")



def inject_images(html_content: str, folder_path: Path) -> str:
    """
    HTML 컨텐츠 내의 로컬 이미지 경로(src="images/...")를 찾아 Base64로 인코딩하여 임베딩합니다.
    Streamlit 등 웹 환경에서 로컬 파일 보안 제약으로 인해 이미지가 보이지 않는 문제를 해결합니다.
    
    Args:
        html_content (str): 원본 HTML 문자열
        folder_path (Path): 이미지가 위치한 기본 폴더 경로
        
    Returns:
        str: 이미지가 Base64로 임베딩된 HTML 문자열
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
                logging.warning(f"이미지 임베딩 실패 ({img_rel_path}): {e}")
                return match.group(0)
        return match.group(0)

    # main.py/core.py에서 생성하는 패턴: src="images/filename.png"
    pattern = r'src="(images/[^"]+)"'
    return re.sub(pattern, replace_match, html_content)

def load_history_from_disk(output_dir: Path = Path("output")) -> list:
    """
    output 디렉토리를 스캔하여 이전 번역 히스토리를 로드합니다.
    폴더명 형식: {filename}_{src}_to_{dest}_{timestamp}
    
    Args:
        output_dir (Path): 스캔할 출력 디렉토리 경로. 기본값은 "output".
        
    Returns:
        list: 히스토리 아이템 딕셔너리의 리스트. 최신순 정렬.
              [{timestamp, results, source, target, engine}, ...]
    """
    history = []
    if not output_dir.exists():
        return history

    # 폴더명 파싱을 위한 정규식 (미리 컴파일하여 효율성 증대)
    # filename에 언더스코어가 포함될 수 있으므로 뒤에서부터 매칭
    # timestamp: YYYYMMDD_HHMMSS (15 chars)
    # lang: 2 chars
    pattern = re.compile(r"^(.*)_([a-z]{2})_to_([a-z]{2})_(\d{8}_\d{6})$")

    for entry in output_dir.iterdir():
        if entry.is_dir():
            match = pattern.match(entry.name)
            if match:
                filename, src, dest, timestamp_str = match.groups()
                
                # 타임스탬프 포맷팅 (가독성 좋게)
                try:
                    dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    display_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    display_time = timestamp_str

                # HTML 파일 확인
                html_path = entry / f"{filename}_interactive.html"
                if html_path.exists():
                    history.append({
                        "timestamp": display_time,
                        "results": [{
                            "filename": filename, # 원본 파일명 (확장자 제외된 stem일 수 있음)
                            "output_dir": str(entry),
                            "html_path": str(html_path)
                        }],
                        "source": src,
                        "target": dest,
                        "engine": "unknown" # 폴더명에는 엔진 정보가 없음
                    })
    
    # 최신순 정렬 (타임스탬프 내림차순)
    history.sort(key=lambda x: x["timestamp"], reverse=True)
    return history

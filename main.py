# argparse: 커맨드 라인 인자를 파싱하기 위해 사용합니다.
# os: 운영 체제와 상호 작용하기 위해 사용합니다. (예: 경로 확인)
# pathlib.Path: 파일 시스템 경로를 객체 지향적으로 다루기 위해 사용합니다.
# logging: 프로그램 실행 중 정보를 기록하기 위해 사용합니다.
import argparse
import os
from pathlib import Path
import logging
from datetime import datetime

import html

# Hugging Face Hub 관련 환경 변수 설정 (심볼릭 링크 비활성화)
os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'

# docling 라이브러리에서 필요한 클래스들을 가져옵니다.
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling_core.types.doc import DoclingDocument, TextItem, TableItem, PictureItem, DocItem

# translator.py에서 구현한 번역 함수들을 가져옵니다.
from translator import translate_by_sentence, translate_text

# 기본 로깅 설정: 시간, 로그 레벨, 메시지 형식을 지정합니다.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HTML_HEADER = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Docling Translation Result</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; }
        .sentence-container { margin-bottom: 12px; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .translated { cursor: pointer; color: #333; font-weight: 500; }
        .translated:hover { color: #0056b3; }
        .original { font-size: 0.95em; color: #666; margin-top: 8px; padding-left: 12px; border-left: 4px solid #ddd; display: none; background-color: #f1f1f1; padding: 8px; border-radius: 4px; }
        img { max-width: 100%; height: auto; display: block; margin: 20px auto; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .caption { text-align: center; font-size: 0.9em; color: #777; margin-top: 10px; }
        h1 { text-align: center; color: #333; margin-bottom: 30px; }
    </style>
    <script>
        function toggleOriginal(el) {
            const next = el.nextElementSibling;
            if (next.style.display === 'none' || next.style.display === '') {
                next.style.display = 'block';
            } else {
                next.style.display = 'none';
            }
        }
    </script>
</head>
<body>
    <h1>Translation Result</h1>
"""

HTML_FOOTER = """
</body>
</html>
"""

def save_and_get_image_path(item: DocItem, doc: DoclingDocument, output_dir: Path, base_filename: str, counters: dict) -> str:
    """
    TableItem 또는 PictureItem의 이미지를 저장하고, 마크다운에서 사용할 상대 경로를 반환합니다.

    :param item: 이미지로 저장할 아이템 (TableItem 또는 PictureItem)
    :param doc: 원본 DoclingDocument 객체
    :param output_dir: 출력을 저장할 디렉토리
    :param base_filename: 출력 파일명의 기반이 될 이름
    :param counters: 테이블과 그림의 번호를 매기기 위한 카운터
    :return: 저장된 이미지의 상대 경로 문자열
    """
    # 아이템 유형에 따라 'table' 또는 'picture' 문자열을 결정합니다.
    item_type = "table" if isinstance(item, TableItem) else "picture"
    counters[item_type] += 1
    
    # 이미지를 저장할 'images' 폴더를 생성합니다. (이미 존재하면 넘어감)
    image_dir = output_dir / "images"
    image_dir.mkdir(exist_ok=True)
    
    # 저장될 이미지 파일의 이름을 결정합니다. (예: 'filename_table_1.png')
    image_filename = f"{base_filename}_{item_type}_{counters[item_type]}.png"
    image_path = image_dir / image_filename
    # 마크다운 파일에서는 항상 슬래시(/)를 사용해야 하므로 경로를 수정합니다.
    relative_path = f"images/{image_filename}"

    try:
        # docling 아이템에서 이미지를 추출합니다.
        img = item.get_image(doc)
        if img:
            # 이미지를 PNG 파일로 저장합니다.
            img.save(image_path, "PNG")
            logging.info(f"이미지 저장 완료: {image_path}")
            return relative_path
    except Exception as e:
        # 이미지 저장 중 오류 발생 시 경고 로그를 남깁니다.
        logging.warning(f"{item.self_ref}의 이미지를 저장할 수 없습니다: {e}")
    
    return ""

def process_document(pdf_path: str, source_lang: str = 'en', target_lang: str = 'ko'):
    """
    PDF를 변환하고, 텍스트 내용을 문장 단위로 번역한 후,
    결과를 고유한 폴더에 마크다운 파일로 저장합니다.

    :param pdf_path: 번역할 PDF 파일 경로
    :param source_lang: 원본 언어 코드 (예: 'en')
    :param target_lang: 목표 언어 코드 (예: 'ko')
    """
    # 1. 입력 파일 유효성 검사
    if not os.path.exists(pdf_path):
        logging.error(f"입력 파일을 찾을 수 없습니다: {pdf_path}")
        return

    # 2. 출력 경로 설정 (동적 생성)
    base_filename = Path(pdf_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 고유한 결과물 폴더 경로 생성
    # 예: output/1706.03762v7/en_to_ko_20251014_183000/
    output_dir = Path("output") / f"{base_filename}_{source_lang}_to_{target_lang}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"문서 처리 시작: {pdf_path} (번역: {source_lang} -> {target_lang})")
    logging.info(f"결과물 저장 폴더: {output_dir}")

    # 3. Docling 변환기 설정 및 실행
    logging.info("Docling 파이프라인 설정 중...")
    pipeline_options = PdfPipelineOptions(generate_picture_images=True, generate_table_images=True, images_scale=2.0)
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )

    logging.info("PDF를 DoclingDocument로 변환 중...")
    try:
        doc: DoclingDocument = converter.convert(pdf_path).document
    except Exception as e:
        logging.error(f"PDF 변환 오류: {e}", exc_info=True)
        return
    logging.info("PDF 변환 성공.")

    # 4. 번역 및 파일 저장
    logging.info("문장 단위 번역과 함께 출력 파일 생성 중...")
    
    # 출력 파일 경로 설정 (언어 코드 동적 반영)
    path_src = output_dir / f"{base_filename}_{source_lang}.md"
    path_target = output_dir / f"{base_filename}_{target_lang}.md"
    path_combined = output_dir / f"{base_filename}_combined.md"
    path_html = output_dir / f"{base_filename}_interactive.html"

    # 이미지 파일명 중복을 피하기 위한 카운터 초기화
    counters = {"table": 0, "picture": 0}

    # 파일을 열어 작업을 진행합니다.
    with open(path_src, "w", encoding="utf-8") as f_src, \
         open(path_target, "w", encoding="utf-8") as f_target, \
         open(path_combined, "w", encoding="utf-8") as f_comb, \
         open(path_html, "w", encoding="utf-8") as f_html:
        
        f_html.write(HTML_HEADER)

        for item, _ in doc.iterate_items():
            page_num_str = f"(p. {item.prov[0].page_no})" if item.prov and item.prov[0].page_no else ""

            if isinstance(item, TextItem):
                if not item.text or not item.text.strip():
                    continue

                # 언어 코드를 전달하여 번역 실행
                sentence_pairs = translate_by_sentence(item.text, src=source_lang, dest=target_lang)
                
                original_paragraph = " ".join([pair[0] for pair in sentence_pairs])
                translated_paragraph = " ".join([pair[1] for pair in sentence_pairs])

                f_src.write(f"{original_paragraph} {page_num_str}\n\n")
                f_target.write(f"{translated_paragraph} {page_num_str}\n\n")

                # 라벨에 동적 언어 코드 사용
                for orig_sent, trans_sent in sentence_pairs:
                    f_comb.write(f"**Original ({source_lang})** {page_num_str}\n\n")
                    f_comb.write(f"{orig_sent}\n\n")
                    f_comb.write(f"**Translated ({target_lang})** {page_num_str}\n\n")
                    f_comb.write(f"{trans_sent}\n\n")
                    f_comb.write("---\n")
                    
                    # HTML 생성
                    orig_safe = html.escape(orig_sent)
                    trans_safe = html.escape(trans_sent)
                    f_html.write(f"""
                    <div class="sentence-container">
                        <div class="translated" onclick="toggleOriginal(this)">{trans_safe} {page_num_str}</div>
                        <div class="original">{orig_safe}</div>
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
                    
                    # HTML 이미지 추가
                    f_html.write(f'<img src="{image_path}" alt="{alt_text}">\n')

                    orig_caption = item.caption_text(doc)
                    if orig_caption:
                        # 캡션 번역 시에도 언어 코드 전달
                        trans_caption = translate_text(orig_caption, src=source_lang, dest=target_lang)
                        
                        # 캡션 라벨에도 동적 언어 코드 사용
                        f_src.write(f"**Caption:** {orig_caption} {page_num_str}\n\n")
                        f_target.write(f"**Caption:** {trans_caption} {page_num_str}\n\n")
                        
                        f_comb.write(f"**Original Caption ({source_lang}):** {orig_caption} {page_num_str}\n\n")
                        f_comb.write(f"> {orig_caption}\n\n")
                        f_comb.write(f"**Translated Caption ({target_lang}):** {trans_caption} {page_num_str}\n\n")
                        f_comb.write(f"> {trans_caption}\n\n")

                        # HTML 캡션 추가
                        f_html.write(f'<div class="caption">{html.escape(trans_caption)}</div>\n')

                    f_comb.write("---\n\n")
        
        f_html.write(HTML_FOOTER)

    logging.info(f"파일 생성 완료: {output_dir}")

# 이 스크립트가 직접 실행될 때만 아래 코드가 동작합니다.
if __name__ == "__main__":
    # 커맨드 라인 인자를 처리하기 위한 ArgumentParser 객체를 생성합니다.
    parser = argparse.ArgumentParser(description="PDF 문서를 문장 단위로 번역합니다.")
    
    # 필수 인자: 번역할 PDF 파일의 경로
    parser.add_argument("pdf_path", type=str, help="번역할 PDF 파일의 경로")
    
    # 선택 인자: 원본 언어 설정
    parser.add_argument('-f', '--from', dest='source_lang', type=str, default='en', 
                        help="번역할 원본 언어 코드 (기본값: en)")
    
    # 선택 인자: 목표 언어 설정
    parser.add_argument('-t', '--to', dest='target_lang', type=str, default='ko', 
                        help="번역 결과물 언어 코드 (기본값: ko)")

    # 커맨드 라인 인자를 파싱합니다.
    args = parser.parse_args()
    
    # 파싱된 인자들을 가지고 메인 함수를 실행합니다.
    process_document(args.pdf_path, args.source_lang, args.target_lang)

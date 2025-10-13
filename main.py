# argparse: 커맨드 라인 인자를 파싱하기 위해 사용합니다.
# os: 운영 체제와 상호 작용하기 위해 사용합니다. (예: 경로 확인)
# pathlib.Path: 파일 시스템 경로를 객체 지향적으로 다루기 위해 사용합니다.
# logging: 프로그램 실행 중 정보를 기록하기 위해 사용합니다.
import argparse
import os
from pathlib import Path
import logging

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

def process_document(pdf_path: str):
    """
    PDF를 변환하고, 텍스트 내용을 문장 단위로 번역한 후,
    네 가지 다른 형식(_en, _ko, _combined, _combined_simple)의 마크다운 파일로 저장합니다.
    """
    # 입력된 PDF 파일 경로가 실제로 존재하는지 확인합니다.
    if not os.path.exists(pdf_path):
        logging.error(f"입력 파일을 찾을 수 없습니다: {pdf_path}")
        return

    logging.info(f"문서 처리 시작: {pdf_path}")
    # 출력 디렉토리('output')를 설정하고 생성합니다.
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    # 출력 파일의 기본 이름을 PDF 파일명에서 추출합니다. (확장자 제외)
    base_filename = Path(pdf_path).stem

    logging.info("Docling 파이프라인 설정 중...")
    # docling 파이프라인 옵션을 설정합니다: 표와 그림을 이미지로 생성하고, 이미지 품질(scale)을 2.0으로 설정합니다.
    pipeline_options = PdfPipelineOptions(generate_picture_images=True, generate_table_images=True, images_scale=2.0)
    # 설정된 옵션으로 DocumentConverter 객체를 생성합니다.
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )

    logging.info("PDF를 DoclingDocument로 변환 중...")
    try:
        # PDF 파일을 docling의 내부 형식인 DoclingDocument로 변환합니다.
        doc: DoclingDocument = converter.convert(pdf_path).document
    except Exception as e:
        # 변환 중 오류 발생 시 에러 로그를 남기고 함수를 종료합니다.
        logging.error(f"PDF 변환 오류: {e}", exc_info=True)
        return
    logging.info("PDF 변환 성공.")

    logging.info("문장 단위 번역과 함께 출력 파일 생성 중...")
    
    # 출력될 4개 마크다운 파일의 전체 경로를 설정합니다.
    path_en = output_dir / f"{base_filename}_en.md"
    path_ko = output_dir / f"{base_filename}_ko.md"
    path_combined = output_dir / f"{base_filename}_combined.md"
    path_combined_simple = output_dir / f"{base_filename}_combined_simple.md"

    # 이미지 파일명 중복을 피하기 위한 카운터를 초기화합니다.
    counters = {"table": 0, "picture": 0}

    # 4개의 파일을 동시에 열어서 작업을 진행합니다. (인코딩은 utf-8)
    with open(path_en, "w", encoding="utf-8") as f_en, \
         open(path_ko, "w", encoding="utf-8") as f_ko, \
         open(path_combined, "w", encoding="utf-8") as f_comb, \
         open(path_combined_simple, "w", encoding="utf-8") as f_comb_simple:

        # DoclingDocument의 모든 아이템(텍스트, 표, 그림 등)을 순회합니다.
        for item, _ in doc.iterate_items():
            # 아이템의 원본 페이지 번호를 추출합니다. (없으면 빈 문자열)
            page_num_str = f"(p. {item.prov[0].page_no})" if item.prov and item.prov[0].page_no else ""

            # 아이템이 텍스트(TextItem)인 경우
            if isinstance(item, TextItem):
                # 텍스트가 비어있지 않은 경우에만 처리합니다.
                if not item.text or not item.text.strip():
                    continue

                # 텍스트 블록을 문장 단위로 번역하여 (원본, 번역) 쌍의 리스트를 받습니다.
                sentence_pairs = translate_by_sentence(item.text)
                
                # 원문(_en.md)과 번역문(_ko.md) 파일에는 전체 문단을 다시 합쳐서 씁니다.
                original_paragraph = " ".join([pair[0] for pair in sentence_pairs])
                translated_paragraph = " ".join([pair[1] for pair in sentence_pairs])

                f_en.write(f"{original_paragraph} {page_num_str}\n\n")
                f_ko.write(f"{translated_paragraph} {page_num_str}\n\n")

                # 통합본(_combined.md) 파일에는 인용구(>)를 사용하여 문장 단위로 번갈아 씁니다.
                for orig_sent, trans_sent in sentence_pairs:
                    f_comb.write(f"**Original (English)** {page_num_str}\n")
                    f_comb.write(f"> {orig_sent}\n\n")
                    f_comb.write(f"**Translated (Korean)** {page_num_str}\n")
                    f_comb.write(f"> {trans_sent}\n\n")
                    f_comb.write("---\n")
                f_comb.write("\n")

                # 실험적인 심플 통합본(_combined_simple.md) 파일에는 인용구 없이 씁니다.
                for orig_sent, trans_sent in sentence_pairs:
                    f_comb_simple.write(f"**Original (English)** {page_num_str}\n")
                    f_comb_simple.write(f"{orig_sent}\n\n")
                    f_comb_simple.write(f"**Translated (Korean)** {page_num_str}\n")
                    f_comb_simple.write(f"{trans_sent}\n\n")
                    f_comb_simple.write("---\n")
                f_comb_simple.write("\n")

            # 아이템이 표(TableItem) 또는 그림(PictureItem)인 경우
            elif isinstance(item, (TableItem, PictureItem)):
                # 아이템을 이미지로 저장하고 상대 경로를 받아옵니다.
                image_path = save_and_get_image_path(item, doc, output_dir, base_filename, counters)
                
                if image_path:
                    # 마크다운 이미지 링크를 생성합니다.
                    alt_text = "table" if isinstance(item, TableItem) else "image"
                    md_link = f"![{alt_text}]({image_path}) {page_num_str}\n\n"
                    
                    # 4개 파일 모두에 이미지 링크를 씁니다.
                    f_en.write(md_link)
                    f_ko.write(md_link)
                    f_comb.write(md_link)
                    f_comb_simple.write(md_link)

                    # 캡션(설명)이 있는 경우, 캡션도 번역하여 추가합니다.
                    orig_caption = item.caption_text(doc)
                    if orig_caption:
                        trans_caption = translate_text(orig_caption) # 캡션은 문장 단위가 아닌 통으로 번역
                        f_en.write(f"**Caption:** {orig_caption} {page_num_str}\n\n")
                        f_ko.write(f"**캡션:** {trans_caption} {page_num_str}\n\n")
                        
                        # 통합본 파일에 캡션 원문과 번역문을 씁니다.
                        f_comb.write(f"**Original Caption:** {orig_caption} {page_num_str}\n")
                        f_comb.write(f"> {orig_caption}\n\n")
                        f_comb.write(f"**Translated Caption:** {trans_caption} {page_num_str}\n")
                        f_comb.write(f"> {trans_caption}\n\n")

                        # 심플 통합본 파일에도 캡션을 씁니다.
                        f_comb_simple.write(f"**Original Caption:** {orig_caption} {page_num_str}\n")
                        f_comb_simple.write(f"{orig_caption}\n\n")
                        f_comb_simple.write(f"**Translated Caption:** {trans_caption} {page_num_str}\n")
                        f_comb_simple.write(f"{trans_caption}\n\n")

                    f_comb.write("---\n\n")
                    f_comb_simple.write("---\n\n")

    logging.info(f"파일 생성 완료: {output_dir}")

# 이 스크립트가 직접 실행될 때만 아래 코드가 동작합니다.
if __name__ == "__main__":
    # 커맨드 라인 인자를 처리하기 위한 ArgumentParser 객체를 생성합니다.
    parser = argparse.ArgumentParser(description="PDF 문서를 문장 단위로 번역합니다.")
    # 'pdf_path'라는 이름의 필수 인자를 추가합니다.
    parser.add_argument("pdf_path", type=str, help="번역할 PDF 파일의 경로")
    # 커맨드 라인 인자를 파싱합니다.
    args = parser.parse_args()
    # 파싱된 인자(pdf_path)를 가지고 메인 함수를 실행합니다.
    process_document(args.pdf_path)

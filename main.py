"""
main.py
=======
Docling PDF 번역기의 CLI(Command Line Interface) 진입점입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **명령줄 인수 파싱**: `argparse`를 사용하여 파일 경로, 언어 설정, 엔진 선택 등의 인수를 받습니다.
2.  **문서 처리 요청**: `src.core.process_document`를 호출하여 문서 변환 및 번역을 실행합니다.
3.  **결과 출력**: 처리 결과를 콘솔에 출력합니다.

사용 예시:
    python main.py document.pdf --source en --target ko --engine google
"""

import argparse
import logging
from src.core import process_document, create_converter

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """
    CLI 메인 함수입니다.
    """
    parser = argparse.ArgumentParser(description="Docling PDF Translator CLI")
    
    # 필수 인수: 입력 파일 경로
    parser.add_argument("input_file", help="Path to the input file (PDF, DOCX, PPTX, etc.)")
    
    # 선택 인수
    parser.add_argument("--source", default="en", help="Source language code (default: en)")
    parser.add_argument("--target", default="ko", help="Target language code (default: ko)")
    parser.add_argument("--engine", default="google", choices=["google", "deepl", "gemini", "openai"], help="Translation engine (default: google)")
    parser.add_argument("--workers", type=int, default=8, help="Number of parallel workers (default: 8)")

    args = parser.parse_args()

    # Converter 생성
    converter = create_converter()

    # 문서 처리 실행
    result = process_document(
        file_path=args.input_file,
        converter=converter,
        source_lang=args.source,
        dest_lang=args.target,
        engine=args.engine,
        max_workers=args.workers
    )

    if result:
        print(f"Successfully processed: {args.input_file}")
        print(f"Output directory: {result['output_dir']}")
        print(f"HTML file: {result['html_path']}")
    else:
        print("Processing failed.")
        exit(1)

if __name__ == "__main__":
    main()

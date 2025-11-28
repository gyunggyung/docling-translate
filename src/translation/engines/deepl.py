"""
src/translation/engines/deepl.py
================================
DeepL 번역 엔진(공식 API) 구현체입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **DeepL 번역**: `deepl` 공식 라이브러리를 사용하여 고품질 번역을 수행합니다.
2.  **API 키 관리**: `DEEPL_API_KEY` 환경 변수를 사용하여 인증합니다.
"""

import os
import logging
import deepl
from ..base import BaseTranslator
from ..utils import to_deepl_lang

class DeepLTranslator(BaseTranslator):
    """
    DeepL 공식 API를 사용하는 번역 엔진 구현체입니다.
    DEEPL_API_KEY 환경 변수가 필요합니다.
    """
    
    def __init__(self):
        """
        DeepL 클라이언트를 초기화합니다. API 키가 없으면 경고를 로그에 남깁니다.
        """
        self.api_key = os.getenv("DEEPL_API_KEY", "").strip()
        self.client = None
        if self.api_key:
            try:
                self.client = deepl.DeepLClient(self.api_key)
            except Exception as e:
                logging.warning(f"DeepL Client Init Failed: {e}")

    def translate(self, text: str, src: str, dest: str) -> str:
        """
        DeepL API를 호출하여 텍스트를 번역합니다.
        """
        if not text or not text.strip():
            return ""
        
        if not self.client:
            logging.error("DeepL API Key missing or client init failed.")
            return text

        try:
            # DeepL 언어 코드로 변환 (예: en -> EN-US)
            source_lang = to_deepl_lang(src)
            target_lang = to_deepl_lang(dest) or "EN-US" # 기본값 영어(미국)

            result = self.client.translate_text(
                text,
                source_lang=source_lang,
                target_lang=target_lang,
            )
            return result.text
        except Exception as e:
            logging.error(f"DeepL Translation Error: {e}")
            return text

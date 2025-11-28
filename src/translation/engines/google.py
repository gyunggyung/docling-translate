"""
src/translation/engines/google.py
=================================
Google 번역 엔진(무료 API) 구현체입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **Google 번역**: `deep-translator` 라이브러리를 사용하여 텍스트를 번역합니다.
2.  **폴백**: 다른 유료 엔진(Gemini, OpenAI 등)의 폴백(Fallback) 엔진으로도 사용됩니다.
"""

from deep_translator import GoogleTranslator as DeepGoogleTranslator
from ..base import BaseTranslator

class GoogleTranslator(BaseTranslator):
    """
    deep-translator 라이브러리를 사용한 Google 번역 엔진 구현체입니다.
    무료 API를 사용하므로 사용량 제한이 있을 수 있습니다.
    """
    
    def translate(self, text: str, src: str, dest: str) -> str:
        """
        Google 번역 API를 호출하여 텍스트를 번역합니다.
        """
        if not text or not text.strip():
            return ""
        try:
            return DeepGoogleTranslator(source=src, target=dest).translate(text)
        except Exception:
            # 실패 시 원문 반환 (또는 로깅 후 빈 문자열)
            # 여기서는 사용자 경험을 위해 원문을 반환하는 정책을 따름
            return text

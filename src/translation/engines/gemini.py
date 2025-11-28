"""
src/translation/engines/gemini.py
=================================
Google Gemini 번역 엔진 구현체입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **Gemini 번역**: `google-genai` 라이브러리를 사용하여 LLM 기반 번역을 수행합니다.
2.  **프롬프트 엔지니어링**: 번역 품질을 높이고 형식을 유지하기 위한 프롬프트를 구성합니다.
3.  **재시도 및 폴백**: API 호출 실패 시 재시도하거나 Google 번역(무료)으로 폴백합니다.
"""

import os
import time
import logging
from ..base import BaseTranslator
from .google import GoogleTranslator
from ..utils import LANGUAGE_NAMES

try:
    from google import genai
except ImportError:
    genai = None

class GeminiTranslator(BaseTranslator):
    """
    Google Gemini API를 사용하는 번역 엔진 구현체입니다.
    GEMINI_API_KEY 또는 GOOGLE_API_KEY 환경 변수가 필요합니다.
    실패 시 GoogleTranslator(무료)로 폴백합니다.
    """
    
    def __init__(self):
        """
        Gemini 클라이언트를 초기화합니다.
        """
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.client = None
        if genai and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logging.warning(f"Gemini Client Init Failed: {e}")
        
        self.fallback_engine = GoogleTranslator()

    def translate(self, text: str, src: str, dest: str) -> str:
        """
        Gemini 모델(gemini-2.5-flash)을 사용하여 번역을 수행합니다.
        재시도 로직(Retry)과 폴백(Fallback) 메커니즘을 포함합니다.
        """
        if not text or not text.strip():
            return ""

        if not self.client:
            return self.fallback_engine.translate(text, src, dest)

        src_name = LANGUAGE_NAMES.get(src, src)
        dest_name = LANGUAGE_NAMES.get(dest, dest)

        # 최대 3회 재시도
        for attempt in range(3):
            try:
                prompt = (
                    f"Translate the text from {src_name} to {dest_name}.\n"
                    f"Maintain technical terms and formatting.\n"
                    f"Do not include the XML tags in your response.\n"
                    f"Return only the translation.\n\n"
                    f"<text>\n{text}\n</text>"
                )

                resp = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )

                if hasattr(resp, "text") and resp.text:
                    result = resp.text.strip()
                    # XML 태그 제거 (프롬프트 지시사항 보완)
                    result = result.replace("<text>", "").replace("</text>", "").strip()
                    return result
                
                raise RuntimeError("Empty response from Gemini")

            except Exception as e:
                msg = str(e)
                # 재시도 가능한 에러인지 확인
                retriable = "503" in msg or "429" in msg or "overloaded" in msg.lower() or "RESOURCE_EXHAUSTED" in msg
                
                if retriable and attempt < 2:
                    time.sleep(2 ** attempt) # 지수 백오프
                    continue
                
                logging.error(f"Gemini Error (Fallback to Google): {e}")
                break
        
        # 모든 시도 실패 시 폴백 엔진 사용
        return self.fallback_engine.translate(text, src, dest)

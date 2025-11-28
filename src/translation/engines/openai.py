"""
src/translation/engines/openai.py
=================================
OpenAI GPT 번역 엔진 구현체입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **GPT 번역**: `openai` 라이브러리를 사용하여 LLM 기반 번역을 수행합니다.
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
    from openai import OpenAI
except ImportError:
    OpenAI = None

class OpenAITranslator(BaseTranslator):
    """
    OpenAI GPT 모델을 사용하는 번역 엔진 구현체입니다.
    OPENAI_API_KEY 환경 변수가 필요합니다.
    실패 시 GoogleTranslator(무료)로 폴백합니다.
    """
    
    def __init__(self):
        """
        OpenAI 클라이언트를 초기화합니다.
        """
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.client = None
        if OpenAI and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logging.warning(f"OpenAI Client Init Failed: {e}")
        
        self.fallback_engine = GoogleTranslator()

    def translate(self, text: str, src: str, dest: str) -> str:
        """
        GPT 모델(gpt-5-nano)을 사용하여 번역을 수행합니다.
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

                response = self.client.responses.create(
                    model="gpt-5-nano",
                    input=prompt
                )

                if hasattr(response, 'output_text') and response.output_text:
                    result = response.output_text.strip()
                    result = result.replace("<text>", "").replace("</text>", "").strip()
                    return result
                
                raise RuntimeError("Empty response from OpenAI")

            except Exception as e:
                msg = str(e)
                retriable = "429" in msg or "503" in msg or "rate_limit" in msg.lower() or "overloaded" in msg.lower()
                
                if retriable and attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                
                logging.error(f"OpenAI Error (Fallback to Google): {e}")
                break
        
        return self.fallback_engine.translate(text, src, dest)

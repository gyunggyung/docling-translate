"""
src/translation/utils.py
========================
번역 관련 유틸리티 함수들을 모아둔 모듈입니다.
"""

from typing import Optional
from .base import BaseTranslator

# 언어 코드 → 언어명 매핑 (OpenAI/Gemini 프롬프트 명확화용)
LANGUAGE_NAMES = {
    'en': 'English',
    'ko': 'Korean',
    'ja': 'Japanese',
    'zh': 'Chinese',
    'fr': 'French',
    'de': 'German',
    'es': 'Spanish',
    'ru': 'Russian',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'auto': 'the source language',
}

def to_deepl_lang(code: str | None) -> str | None:
    """우리 프로젝트 언어코드(en, ko, ja ...)를 DeepL 코드(EN, KO, JA ...)로 변환"""
    if not code:
        return None
    code = code.lower()

    # 자주 쓰는 건 명시적으로
    mapping = {
        "en": "EN",
        "en-us": "EN-US",
        "en-gb": "EN-GB",
        "ko": "KO",
        "ja": "JA",
        "zh": "ZH",
    }
    if code in mapping:
        return mapping[code]

    # 나머지는 앞 2글자 대문자로 (예: 'fr' -> 'FR')
    if "-" in code:
        return code.upper()
    return code[:2].upper()

def get_translator(engine: str = 'google') -> BaseTranslator:
    """
    지정된 엔진에 해당하는 번역기 인스턴스를 반환합니다.

    Args:
        engine (str): 번역 엔진 이름 ('google', 'deepl', 'gemini', 'openai', 'qwen', 'qwen-0.6b')

    Returns:
        BaseTranslator: 번역기 인스턴스
    """
    if engine == 'google':
        from .engines.google import GoogleTranslator
        return GoogleTranslator()
    elif engine == 'deepl':
        from .engines.deepl import DeepLTranslator
        return DeepLTranslator()
    elif engine == 'gemini':
        from .engines.gemini import GeminiTranslator
        return GeminiTranslator()
    elif engine == 'openai':
        from .engines.openai import OpenAITranslator
        return OpenAITranslator()
    elif engine == 'qwen' or engine == 'qwen-0.6b':
        from .engines.qwen import QwenTranslator
        return QwenTranslator()
    else:
        raise ValueError(f"Unknown engine: {engine}")

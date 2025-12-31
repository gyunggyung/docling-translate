"""
src/translation/__init__.py
===========================
번역 엔진 패키지의 초기화 모듈입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **팩토리 함수 제공**: 엔진 이름(문자열)을 입력받아 해당 번역 엔진 인스턴스를 생성하는 `create_translator` 함수를 제공합니다.
2.  **엔진 등록**: 지원되는 번역 엔진 클래스들을 매핑하여 관리합니다.
"""

from .base import BaseTranslator
from .engines.google import GoogleTranslator
from .engines.deepl import DeepLTranslator
from .engines.gemini import GeminiTranslator
from .engines.openai import OpenAITranslator
from .engines.qwen import QwenTranslator
from .engines.lfm2 import LFM2Translator
from .engines.lfm2_koen import LFM2KOENTranslator
from .engines.nllb import NLLBTranslator
from .engines.nllb_koen import NLLBKOENTranslator
from .engines.yanolja import YanoljaTranslator

def create_translator(engine_name: str) -> BaseTranslator:
    """
    지정된 이름의 번역 엔진 인스턴스를 생성하여 반환합니다.
    
    Args:
        engine_name (str): 번역 엔진 이름 ('google', 'deepl', 'gemini', 'openai', 'qwen', 'yanolja')
        
    Returns:
        BaseTranslator: 생성된 번역 엔진 인스턴스
        
    Raises:
        ValueError: 지원하지 않는 엔진 이름일 경우 발생
    """
    engines = {
        "google": GoogleTranslator,
        "deepl": DeepLTranslator,
        "gemini": GeminiTranslator,
        "openai": OpenAITranslator,
        "qwen": QwenTranslator,
        "qwen-0.6b": QwenTranslator,
        "lfm2": LFM2Translator,
        "lfm2-koen-mt": LFM2KOENTranslator,
        "nllb": NLLBTranslator,
        "nllb-koen": NLLBKOENTranslator,
        "yanolja": YanoljaTranslator,
    }
    
    engine_class = engines.get(engine_name.lower())
    if not engine_class:
        raise ValueError(f"Unsupported engine: {engine_name}")
    
    return engine_class()

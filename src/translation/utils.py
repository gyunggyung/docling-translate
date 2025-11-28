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

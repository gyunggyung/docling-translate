# translator.py
# 번역 엔진들을 한 곳에서 관리하는 모듈입니다.

import os
import time
import logging
import concurrent.futures
from typing import List, Tuple  # (지금은 거의 안 쓰지만, 일단 유지)

from deep_translator import GoogleTranslator  # deep-translator 기반
import deepl
import nltk  # 문장 단위 분리를 위한 NLTK

# Gemini SDK는 선택 사항이므로, 설치 안 돼 있으면 None 처리
try:
    from google import genai  # google-genai 공식 SDK
except ImportError:
    genai = None

# 기본 로깅 설정
logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

# ------------------------------
# 전역 설정 (환경 변수)
# ------------------------------

# 번역 엔진 선택은 이제 main.py 인자로 받으므로,
# 여기서는 엔진 전역(ENGINE)은 더 이상 사용하지 않는다.

# DeepL / Gemini API 키
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "").strip()

_deepl_client = None
if DEEPL_API_KEY:
    _deepl_client = deepl.DeepLClient(DEEPL_API_KEY)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# ------------------------------
# NLTK 모델 준비
# ------------------------------
try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    _log.info("NLTK 데이터 모델이 없거나 불완전합니다. 'punkt'와 'punkt_tab'을 다운로드합니다...")
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)
    _log.info("NLTK 모델 다운로드가 완료되었습니다.")


# ------------------------------
# 엔진별 로우레벨 번역 함수
# ------------------------------

def _translate_with_google(text: str, src: str, dest: str) -> str:
    """deep-translator의 GoogleTranslator 사용"""
    return GoogleTranslator(source=src, target=dest).translate(text)


def _to_deepl_lang(code: str | None) -> str | None:
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


def _translate_with_deepl(text: str, src: str, dest: str) -> str:
    """공식 DeepL Python SDK로 번역"""
    if not _deepl_client or not DEEPL_API_KEY:
        _log.error("DeepL 클라이언트가 초기화되지 않았습니다. DEEPL_API_KEY 환경 변수를 확인하세요.")
        return text

    try:
        source_lang = _to_deepl_lang(src)
        target_lang = _to_deepl_lang(dest) or "EN"

        result = _deepl_client.translate_text(
            text,
            source_lang=source_lang,  # None이면 자동 감지
            target_lang=target_lang,
        )
        return result.text
    except deepl.DeepLException as e:
        _log.error("공식 DeepL API 번역 중 오류 발생: %s", e)
        return text
    except Exception as e:
        _log.error("예상치 못한 DeepL 오류: %s", e)
        return text


def _translate_with_gemini(text: str, src: str, dest: str) -> str:
    """
    Gemini로 번역을 시도하되,
    - 503 / 429 같은 에러가 나면 몇 번 재시도
    - 그래도 안 되면 Google 번역으로 fallback
    """
    # SDK 자체가 없는 경우 → 바로 Google로 fallback
    if genai is None:
        _log.error(
            "google-genai 패키지가 설치되어 있지 않아 Gemini를 사용할 수 없습니다. "
            "Google 번역으로 fallback 합니다."
        )
        return _translate_with_google(text, src, dest)

    if not GEMINI_API_KEY:
        _log.error("GEMINI_API_KEY가 설정되어 있지 않아 Gemini를 사용할 수 없습니다.")
        return text

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        _log.error("Gemini 클라이언트 초기화 실패, Google로 fallback: %s", e)
        return _translate_with_google(text, src, dest)

    # 최대 3번까지 재시도 (0,1,2번째 시도)
    last_error = None
    for attempt in range(3):
        try:
            prompt = (
                f"Translate the following text from {src} to {dest}.\n"
                f"Return only the translated text, without quotes.\n\n"
                f"{text}"
            )

            resp = client.models.generate_content(
                model="gemini-2.5-flash",   # 현재 사용 중인 모델명
                contents=prompt,
            )

            # 정상 응답
            if hasattr(resp, "text") and resp.text:
                return resp.text.strip()

            # text가 비어 있는 희한한 경우 → 에러 취급하고 재시도
            raise RuntimeError("Gemini 응답에 text가 없습니다.")

        except Exception as e:
            last_error = e
            msg = str(e)

            # 503 / 429 같이 "잠깐 과부하 / quota" 느낌이면 재시도
            retriable = (
                "503" in msg
                or "UNAVAILABLE" in msg
                or "model is overloaded" in msg.lower()
                or "RESOURCE_EXHAUSTED" in msg
                or "429" in msg
            )

            if retriable and attempt < 2:
                wait = 2 ** attempt  # 1초 → 2초 → 4초
                _log.warning(
                    "Gemini 호출 실패(시도 %d/3, %ss 후 재시도): %s",
                    attempt + 1,
                    wait,
                    msg,
                )
                time.sleep(wait)
                continue  # 다음 시도

            # 재시도 불가하거나 마지막 시도면 루프 종료
            _log.error("Gemini 번역 최종 실패, Google로 fallback: %s", msg)
            break

    # 여기까지 왔다는 건 3번 모두 실패했다는 뜻 → Google 번역으로 fallback
    return _translate_with_google(text, src, dest)


# ------------------------------
# 공개 함수: translate_text / translate_by_sentence
# ------------------------------

def translate_text(
    text: str,
    src: str,
    dest: str,
    engine: str = "google",
) -> str:
    """
    주어진 단일 텍스트 문자열을 번역합니다.

    engine 인자로 사용할 수 있는 값:
      - "google" (기본값)
      - "deepl"
      - "gemini"
    """
    if not text or not text.strip():
        return ""

    engine = (engine or "google").lower()
    translated: str | None

    try:
        if engine == "google":
            translated = _translate_with_google(text, src, dest)
        elif engine == "deepl":
            translated = _translate_with_deepl(text, src, dest)
        elif engine == "gemini":
            translated = _translate_with_gemini(text, src, dest)
        else:
            _log.warning(
                f"알 수 없는 번역 엔진 '{engine}' 이므로 google로 fallback 합니다."
            )
            translated = _translate_with_google(text, src, dest)

        return translated if translated is not None else ""
    except Exception as e:
        _log.error(f"번역 중 오류 발생({engine}): {e}", exc_info=True)
        # 문제 생기면 원문을 그대로 돌려주도록 함
        return text


def translate_by_sentence(
    text: str,
    src: str,
    dest: str,
    engine: str = "google",
    max_workers: int = 1,
) -> list[tuple[str, str]]:
    """
    텍스트를 문장 단위로 분리하여 병렬로 번역합니다.
    
    Args:
        text (str): 번역할 전체 텍스트
        src (str): 원본 언어 코드
        dest (str): 대상 언어 코드
        engine (str): 번역 엔진 ('google', 'deepl', 'gemini')
        max_workers (int): 병렬 처리를 위한 워커 수
        
    Returns:
        list[tuple[str, str]]: (원문 문장, 번역된 문장) 튜플의 리스트
    """
    if not text or not text.strip():
        return []

    sentences = nltk.sent_tokenize(text)
    if len(sentences) > 1:
        logging.info(f"Translating batch of {len(sentences)} sentences")
    results = []

    # 워커 수가 1 이하이면 순차 처리 (오버헤드 감소 및 디버깅 용이)
    if max_workers <= 1:
        for sentence in sentences:
            translated_sentence = translate_text(sentence, src, dest, engine=engine)
            results.append((sentence, translated_sentence))
        return results

    # 병렬 처리
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # executor.map은 입력 순서대로 결과를 반환하므로 적합함
        try:
            # map 함수는 iterable의 각 요소에 함수를 적용하고 결과를 순서대로 반환
            translated_sentences = list(executor.map(
                lambda s: translate_text(s, src, dest, engine),
                sentences
            ))
            
            for original, translated in zip(sentences, translated_sentences):
                results.append((original, translated))
                
        except Exception as e:
            _log.error(f"병렬 번역 중 오류 발생: {e}")
            # 오류 발생 시 빈 리스트 반환
            return []

    return results


def translate_sentences_bulk(
    sentences: list[str],
    src: str,
    dest: str,
    engine: str = "google",
    max_workers: int = 1,
) -> list[str]:
    """
    다수의 문장을 병렬로 번역하여 반환합니다. (Bulk Translation)
    
    Args:
        sentences (list[str]): 번역할 문장 리스트
        src (str): 원본 언어 코드
        dest (str): 대상 언어 코드
        engine (str): 번역 엔진
        max_workers (int): 병렬 처리를 위한 워커 수
        
    Returns:
        list[str]: 번역된 문장 리스트 (입력 순서 유지)
    """
    if not sentences:
        return []

    # 워커 수가 1 이하이면 순차 처리
    if max_workers <= 1:
        return [translate_text(s, src, dest, engine) for s in sentences]

    # 병렬 처리
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        try:
            # map을 사용하여 입력 순서대로 결과 반환
            return list(executor.map(
                lambda s: translate_text(s, src, dest, engine),
                sentences
            ))
        except Exception as e:
            _log.error(f"Bulk 병렬 번역 중 오류 발생: {e}")
            # 오류 발생 시 순차 처리로 폴백
            return [translate_text(s, src, dest, engine) for s in sentences]

# 필요한 라이브러리들을 가져옵니다.
from deep_translator import GoogleTranslator # 구글 번역을 위한 라이브러리
import logging # 로그 기록을 위한 라이브러리
import nltk # 자연어 처리를 위한 NLTK 라이브러리

# 기본 로깅 설정
logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

try:
    # NLTK의 문장 토큰화에 필요한 리소스가 있는지 확인합니다.
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    # 리소스가 없는 경우, 사용자에게 알리고 다운로드를 시작합니다.
    _log.info("NLTK 데이터 모델이 없거나 불완전합니다. 'punkt'와 'punkt_tab'을 다운로드합니다...")
    # 오류 메시지의 제안에 따라 리소스를 다운로드합니다. (quiet=True로 설정하여 불필요한 로그 최소화)
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    _log.info("NLTK 모델 다운로드가 완료되었습니다.")

def translate_text(text: str, src: str = "en", dest: str = "ko") -> str:
    """
    주어진 단일 텍스트 문자열을 번역합니다.
    번역에 실패하거나 텍스트가 비어있으면 원본 텍스트를 반환합니다.

    :param text: 번역할 텍스트
    :param src: 원본 언어 코드 (기본값: 'en')
    :param dest: 대상 언어 코드 (기본값: 'ko')
    :return: 번역된 텍스트 또는 원본 텍스트
    """
    # 입력된 텍스트가 비어있거나 공백만 있는지 확인합니다.
    if not text or not text.strip():
        return ""
    try:
        # GoogleTranslator 객체를 생성하고 텍스트를 번역합니다.
        translated = GoogleTranslator(source=src, target=dest).translate(text)
        # 번역 결과가 있으면 결과를, 없으면 빈 문자열을 반환합니다.
        return translated if translated else ""
    except Exception as e:
        # 번역 중 오류가 발생하면 로그를 남기고 원본 텍스트를 반환합니다.
        _log.error(f"번역 중 오류 발생: {e}")
        return text  # 오류 발생 시 원본 텍스트로 대체

def translate_by_sentence(text: str, src: str = "en", dest: str = "ko") -> list[tuple[str, str]]:
    """
    주어진 텍스트 블록을 문장 단위로 나누고, 각 문장을 번역합니다.
    결과를 (원본 문장, 번역된 문장) 형태의 튜플 리스트로 반환합니다.

    :param text: 번역할 텍스트 블록
    :param src: 원본 언어 코드 (기본값: 'en')
    :param dest: 대상 언어 코드 (기본값: 'ko')
    :return: (원본 문장, 번역된 문장) 튜플의 리스트
    """
    # 입력된 텍스트가 비어있거나 공백만 있는지 확인합니다.
    if not text or not text.strip():
        return []

    # NLTK를 사용하여 텍스트를 문장 단위로 분리합니다.
    sentences = nltk.sent_tokenize(text)
    
    translated_pairs = [] # 번역된 (원본, 번역) 쌍을 저장할 리스트
    # 각 문장에 대해 반복 작업을 수행합니다.
    for sentence in sentences:
        # 문장이 공백이 아닌 경우에만 번역을 수행합니다.
        if sentence.strip():
            # 위에서 정의한 translate_text 함수를 사용해 문장을 번역합니다.
            translated_sentence = translate_text(sentence, src, dest)
            # 원본 문장과 번역된 문장을 튜플로 묶어 리스트에 추가합니다.
            translated_pairs.append((sentence, translated_sentence))
    
    return translated_pairs
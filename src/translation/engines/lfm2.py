"""
src/translation/engines/lfm2.py
===============================
LiquidAI LFM2-1.2B-GGUF 모델을 사용하는 번역 엔진 모듈입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **모델 로드**: `huggingface_hub`를 통해 GGUF 모델을 다운로드하고 `llama_cpp`로 로드합니다.
2.  **번역 수행**: 단순한 Completion 프롬프트 형식을 사용하여 텍스트를 번역합니다.
"""

import re
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

from ..base import BaseTranslator
from ..utils import LANGUAGE_NAMES

class LFM2Translator(BaseTranslator):
    """
    LiquidAI LFM2-1.2B-GGUF 모델을 사용하는 번역기입니다.
    """

    def __init__(self):
        """
        LFM2Translator를 초기화합니다.
        필요한 모델 파일을 다운로드하고 Llama 인스턴스를 생성합니다.
        """
        if Llama is None:
            raise ImportError(
                "llama-cpp-python이 설치되지 않았습니다. "
                "`pip install llama-cpp-python huggingface_hub`을 실행해주세요."
            )
        
        try:
            from huggingface_hub import hf_hub_download
        except ImportError:
             raise ImportError(
                "huggingface_hub가 설치되지 않았습니다. "
                "`pip install huggingface_hub`을 실행해주세요."
            )

        print("LFM2-1.2B-GGUF 모델을 로드하는 중입니다...")
        
        # 모델 다운로드 (캐시된 경우 다운로드 생략)
        # repo_id: LiquidAI/LFM2-1.2B-GGUF
        # filename: LFM2-1.2B-Q4_K_M.gguf
        self.model_path = hf_hub_download(
            repo_id="LiquidAI/LFM2-1.2B-GGUF",
            filename="LFM2-1.2B-Q4_K_M.gguf"
        )
        
        # Llama 인스턴스 생성
        # n_ctx: 4096 (긴 문맥 처리를 위해 설정)
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=4096,
            verbose=False # 로그 출력 끄기
        )
        print("LFM2-1.2B-GGUF 모델 로드 완료.")

    def translate(self, text: str, src: str, dest: str) -> str:
        """
        LFM2 모델을 사용하여 텍스트를 번역합니다.

        Args:
            text (str): 번역할 텍스트
            src (str): 원본 언어 코드
            dest (str): 대상 언어 코드

        Returns:
            str: 번역된 텍스트
        """
        # 언어 코드를 전체 이름으로 변환 (예: 'en' -> 'English')
        src_name = LANGUAGE_NAMES.get(src, src)
        dest_name = LANGUAGE_NAMES.get(dest, dest)

        # 단순 Completion 프롬프트 구성
        # 특수 토큰(<|im_start|> 등) 의존성을 제거하여 토크나이징 문제 방지
        prompt = f"""Translate the following text from {src_name} to {dest_name}.

Text:
{text}

Translation:"""
        
        try:
            # 생성 요청 (text completion 사용)
            output = self.llm(
                prompt,
                max_tokens=4096,
                stop=["\n\n", "Text:", "Translation:"], # 정지 조건 설정
                temperature=0.3,
                top_p=0.9,
                echo=False # 프롬프트는 출력에 포함하지 않음
            )
            
            # 결과 추출
            translated_text = output['choices'][0]['text'].strip()
            
        except Exception as e:
            print(f"Error during translation: {e}")
            print(f"Failed text: {text}")
            return text # 실패 시 원문 반환
        
        # 후처리: 불필요한 따옴표 제거 (가끔 발생)
        if translated_text.startswith('"') and translated_text.endswith('"'):
            translated_text = translated_text[1:-1]
            
        return translated_text

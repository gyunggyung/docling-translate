"""
src/translation/engines/yanolja.py
==================================
YanoljaNEXT-Rosetta-4B-2511-GGUF 모델을 사용하는 번역 엔진 모듈입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **모델 로드**: `huggingface_hub`를 통해 GGUF 모델을 다운로드하고 `llama_cpp`로 로드합니다.
2.  **번역 수행**: 모델 고유의 프롬프트 형식을 사용하여 텍스트를 번역합니다.
"""

import os
from typing import Optional
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

from ..base import BaseTranslator
from ..utils import LANGUAGE_NAMES

class YanoljaTranslator(BaseTranslator):
    """
    YanoljaNEXT-Rosetta-4B-2511-GGUF 모델을 사용하는 번역기입니다.
    """

    def __init__(self):
        """
        YanoljaTranslator를 초기화합니다.
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

        print("YanoljaNEXT-Rosetta-4B-2511-GGUF 모델을 로드하는 중입니다...")
        
        # 모델 다운로드 (캐시된 경우 다운로드 생략)
        # repo_id: yanolja/YanoljaNEXT-Rosetta-4B-2511-GGUF
        # filename: Q5_K_M/YanoljaNEXT-Rosetta-4B-2511-bf16-q5_k_m.gguf (Q5_K_M 권장)
        self.model_path = hf_hub_download(
            repo_id="yanolja/YanoljaNEXT-Rosetta-4B-2511-GGUF",
            filename="Q5_K_M/YanoljaNEXT-Rosetta-4B-2511-bf16-q5_k_m.gguf"
        )
        
        # CPU 물리 코어 수 계산 (하이퍼스레딩 제외 시 최적 성능)
        physical_cores = os.cpu_count() // 2 if os.cpu_count() else 4
        
        # Llama 인스턴스 생성
        # n_ctx: 4096 (모델 스펙 및 일반적인 문서 청크 크기 고려)
        # n_threads: 물리 코어 수만 사용하여 컨텍스트 스위칭 최소화
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=4096,
            n_threads=physical_cores,
            verbose=False # 로그 출력 끄기
        )
        print(f"YanoljaNEXT-Rosetta-4B-2511-GGUF 모델 로드 완료 ({physical_cores} threads).")

    def translate(self, text: str, src: str, dest: str) -> str:
        """
        Yanolja 모델을 사용하여 텍스트를 번역합니다.

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

        # Yanolja Rosetta 프롬프트 구성
        # <start_of_turn>instruction ... <end_of_turn>
        # <start_of_turn>source ... <end_of_turn>
        # <start_of_turn>translation
        
        prompt = f"""<start_of_turn>instruction
Translate the following text from {src_name} to {dest_name}.
Provide the final translation immediately without any other text.
<end_of_turn>
<start_of_turn>source
{text}
<end_of_turn>
<start_of_turn>translation
"""

        # 생성 요청
        output = self.llm(
            prompt,
            max_tokens=4096, # 출력 최대 토큰 수
            stop=["<end_of_turn>"], # 생성을 멈출 토큰
            echo=False, # 프롬프트 포함 여부
            temperature=0.7, 
            top_p=0.9,
        )

        # 결과 추출
        translated_text = output['choices'][0]['text'].strip()
        
        return translated_text

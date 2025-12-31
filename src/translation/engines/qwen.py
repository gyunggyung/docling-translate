"""
src/translation/engines/qwen.py
===============================
Qwen3-0.6B-GGUF 모델을 사용하는 번역 엔진 모듈입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **모델 로드**: `huggingface_hub`를 통해 GGUF 모델을 다운로드하고 `llama_cpp`로 로드합니다.
2.  **번역 수행**: ChatML 프롬프트 형식을 사용하여 텍스트를 번역합니다.
"""

import os
import re
from typing import Optional
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

from ..base import BaseTranslator
from ..utils import LANGUAGE_NAMES

class QwenTranslator(BaseTranslator):
    """
    Qwen3-0.6B-GGUF 모델을 사용하는 번역기입니다.
    """

    def __init__(self):
        """
        QwenTranslator를 초기화합니다.
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

        print("Qwen3-0.6B-GGUF 모델을 로드하는 중입니다...")
        
        # 모델 다운로드 (캐시된 경우 다운로드 생략)
        # repo_id: bartowski/Qwen_Qwen3-0.6B-GGUF (Q4_K_M 사용)
        self.model_path = hf_hub_download(
            repo_id="bartowski/Qwen_Qwen3-0.6B-GGUF",
            filename="Qwen_Qwen3-0.6B-Q4_K_M.gguf"
        )
        
        # CPU 물리 코어 수 계산 (하이퍼스레딩 제외 시 최적 성능)
        physical_cores = os.cpu_count() // 2 if os.cpu_count() else 4
        
        # Llama 인스턴스 생성
        # n_ctx: 컨텍스트 길이 (Qwen3는 32k까지 지원하지만 로컬 CPU 부하 고려하여 2048~4096 설정)
        # n_threads: 물리 코어 수만 사용하여 컨텍스트 스위칭 최소화
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=2048,
            n_threads=physical_cores,
            verbose=False # 로그 출력 끄기
        )
        print(f"Qwen3-0.6B-GGUF 모델 로드 완료 ({physical_cores} threads).")

    def translate(self, text: str, src: str, dest: str) -> str:
        """
        Qwen3 모델을 사용하여 텍스트를 번역합니다.

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

        # ChatML 프롬프트 구성
        # 시스템 메시지에 번역가 페르소나 부여 및 Thinking Mode 비활성화 (/no_think)
        # 명시적으로 생각 과정을 출력하지 말라고 지시하고, <text> 태그 내부만 번역하도록 유도
        system_prompt = (
            f"You are a professional translator. Translate the following text from {src_name} to {dest_name}. "
            f"The text to translate is wrapped in <text> tags. "
            f"Do not output any thinking process or tags. /no_think"
        )
        
        # 프롬프트 템플릿 적용
        prompt = f"""<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
<text>
{text}
</text><|im_end|>
<|im_start|>assistant
"""

        # 생성 요청
        output = self.llm(
            prompt,
            max_tokens=2048, # 출력 최대 토큰 수
            stop=["<|im_end|>"], # 생성을 멈출 토큰
            echo=False, # 프롬프트 포함 여부
            # Non-thinking mode 권장 파라미터 적용
            temperature=0.7, 
            top_p=0.8,
            top_k=20,
            presence_penalty=1.5
        )

        # 결과 추출
        translated_text = output['choices'][0]['text'].strip()
        
        # 후처리: <think> 태그 및 내용 제거
        translated_text = re.sub(r'<think>.*?</think>', '', translated_text, flags=re.DOTALL).strip()
        
        # 후처리: <text> 태그 제거 (모델이 실수로 출력했을 경우)
        translated_text = translated_text.replace("<text>", "").replace("</text>", "").strip()
        
        return translated_text

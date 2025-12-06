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
        # n_ctx: 2048 (안정성을 위해 조정)
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=2048,
            verbose=False 
        )
        print("LFM2-1.2B-GGUF 모델 로드 완료 (CPU Mode).")

    def translate_batch(self, sentences, src, dest, max_workers=1, progress_cb=None):
        """
        LFM2 모델의 안정성을 위해 ThreadPoolExecutor를 사용하지 않고
        단순 반복문으로 순차 처리를 수행합니다.
        """
        results = []
        total = len(sentences)
        
        print(f"LFM2: Starting serial translation of {total} items...")
        
        for i, text in enumerate(sentences):
            try:
                # 개별 번역 수행
                translated = self.translate(text, src, dest)
                results.append(translated)
            except Exception as e:
                print(f"Batch processing error at index {i}: {e}")
                results.append(text) # 에러 시 원문 반환
            
            # 진행상황 콜백 호출
            if progress_cb:
                progress_cb((i + 1) / total, f"번역 중... ({i + 1}/{total})")
                
        return results

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
        # 컨텍스트 초기화 (필수: 이전 번역 상태가 남으면 decode 에러 발생)
        if hasattr(self.llm, "reset"):
            self.llm.reset()
            
        # 언어 코드를 전체 이름으로 변환 (예: 'en' -> 'English')
        src_name = LANGUAGE_NAMES.get(src, src)
        dest_name = LANGUAGE_NAMES.get(dest, dest)

        # XML 태그를 활용한 엄격한 번역 프롬프트
        # System: 역할 부여 및 태그 사용 지시
        # User: <src>태그로 감싼 원문
        # Assistant: <tgt>태그로 시작을 유도하여 번역만 출력하게 함 (Pre-fill)
        prompt = f"""<|im_start|>system
You are a professional translator. Translate the text from {src_name} to {dest_name}.
Output ONLY the translated text inside <tgt> tags. Do not interpret the text, just translate it.
<|im_end|>
<|im_start|>user
<src>{text}</src><|im_end|>
<|im_start|>assistant
<tgt>"""
        
        try:
            # 생성 요청
            output = self.llm(
                prompt,
                max_tokens=512, 
                stop=["</tgt>", "<|im_end|>"], # 태그 닫힘 또는 턴 종료 시 중단
                temperature=0.1, 
                top_p=0.9,
                echo=False
            )
            
            # 결과 추출 (프롬프트의 <tgt> 뒤에 이어지는 텍스트만 가져옴)
            translated_text = output['choices'][0]['text'].strip()
            
            # 후처리: 태그 제거 (Regex 사용으로 더 강력하게 제거)
            # <src>, <tgt> 및 닫는 태그, 그리고 주변 공백 제거
            translated_text = re.sub(r'</?src>', '', translated_text)
            translated_text = re.sub(r'</?tgt>', '', translated_text)
            translated_text = translated_text.strip()
            
        except Exception as e:
            print(f"Error during translation: {e}")
            return text
        
        # 후처리: 불필요한 따옴표 제거
        if translated_text.startswith('"') and translated_text.endswith('"'):
            translated_text = translated_text[1:-1]
            
        return translated_text

        
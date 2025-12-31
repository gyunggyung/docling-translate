"""
src/translation/engines/lfm2_koen.py
====================================
한국어-영어 전용 번역 엔진 모듈입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **모델 로드**: `huggingface_hub`를 통해 GGUF 모델을 다운로드하고 `llama_cpp`로 로드합니다.
2.  **번역 수행**: 한국어 ↔ 영어 양방향 번역을 위한 간소화된 프롬프트를 사용합니다.

사용 모델: gyung/lfm2-1.2b-koen-mt-v8-rl-10k-merged-GGUF (Q5_K_M, 843MB)
"""

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

from ..base import BaseTranslator


class LFM2KOENTranslator(BaseTranslator):
    """
    한국어-영어 전용 번역기입니다.
    gyung/lfm2-1.2b-koen-mt-v8-rl-10k-merged-GGUF 모델을 사용합니다.
    
    지원 언어:
    - 한국어 (ko) → 영어 (en)
    - 영어 (en) → 한국어 (ko)
    """

    # 지원 언어 (한국어/영어만)
    SUPPORTED_LANGUAGES = {'ko', 'en'}

    def __init__(self):
        """
        LFM2KOENTranslator를 초기화합니다.
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

        print("LFM2-1.2B-KOEN-MT 모델을 로드하는 중입니다...")
        
        # 모델 다운로드 (캐시된 경우 다운로드 생략)
        # repo_id: gyung/lfm2-1.2b-koen-mt-v8-rl-10k-merged-GGUF
        # filename: lfm2-1.2b-koen-mt-v8-rl-10k-merged-Q5_K_M.gguf
        self.model_path = hf_hub_download(
            repo_id="gyung/lfm2-1.2b-koen-mt-v8-rl-10k-merged-GGUF",
            filename="lfm2-1.2b-koen-mt-v8-rl-10k-merged-Q5_K_M.gguf"
        )
        
        # Llama 인스턴스 생성
        # n_ctx: 4096 (문맥 유지를 위해 확장)
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=4096,
            verbose=False 
        )
        print("LFM2-1.2B-KOEN-MT 모델 로드 완료 (CPU Mode).")

    def translate_batch(self, sentences, src, dest, max_workers=1, progress_cb=None):
        """
        LFM2 모델의 안정성을 위해 ThreadPoolExecutor를 사용하지 않고
        단순 반복문으로 순차 처리를 수행합니다.
        """
        results = []
        total = len(sentences)
        
        print(f"LFM2-KOEN-MT: Starting serial translation of {total} items...")
        
        for i, text in enumerate(sentences):
            try:
                # 개별 번역 수행
                translated = self.translate(text, src, dest)
                results.append(translated)
            except Exception as e:
                print(f"Batch processing error at index {i}: {e}")
                results.append(text)  # 에러 시 원문 반환
            
            # 진행상황 콜백 호출
            if progress_cb:
                progress_cb((i + 1) / total, f"({i + 1}/{total})")
                
        return results

    def translate(self, text: str, src: str, dest: str) -> str:
        """
        한국어-영어 전용 번역을 수행합니다.

        Args:
            text (str): 번역할 텍스트
            src (str): 원본 언어 코드 ('ko' 또는 'en')
            dest (str): 대상 언어 코드 ('ko' 또는 'en')

        Returns:
            str: 번역된 텍스트
        """
        # 컨텍스트 초기화 (필수: 이전 번역 상태가 남으면 decode 에러 발생)
        if hasattr(self.llm, "reset"):
            self.llm.reset()
        
        # 대상 언어에 따른 간소화된 프롬프트 선택
        if dest == "ko":
            system = "Translate the following text to Korean."
        else:
            system = "Translate the following text to English."

        # ChatML 포맷 프롬프트
        prompt = f"""<|im_start|>system
{system}<|im_end|>
<|im_start|>user
{text}<|im_end|>
<|im_start|>assistant
"""
        
        try:
            # 생성 요청
            output = self.llm(
                prompt,
                max_tokens=512, 
                stop=["<|im_end|>"],  # 턴 종료 시 중단
                temperature=0.3,  # 약간의 창의성 허용
                min_p=0.15,  # Top-p 대신 min_p 사용 (모델 권장)
                repeat_penalty=1.05,  # 반복 생성 방지
                echo=False
            )
            
            # 결과 추출
            translated_text = output['choices'][0]['text'].strip()
            
            # 후처리: 불필요한 따옴표 제거
            if translated_text.startswith('"') and translated_text.endswith('"'):
                translated_text = translated_text[1:-1]
                
            return translated_text.strip()
            
        except Exception as e:
            print(f"Error during translation: {e}")
            return text

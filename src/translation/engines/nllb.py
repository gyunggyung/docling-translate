"""
src/translation/engines/nllb.py
===============================
Meta NLLB-200 다국어 번역 엔진 모듈입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **모델 로드**: CTranslate2 최적화 버전으로 빠른 로드 및 추론.
2.  **번역 수행**: 200개 언어 지원, 인코더-디코더 구조 기반 고품질 번역.

사용 모델: facebook/nllb-200-distilled-600M (CTranslate2 최적화 버전)

속도 최적화:
- CTranslate2 양자화 모델 (int8) 사용
- 빠른 다운로드 및 추론
"""

try:
    import ctranslate2
    from transformers import AutoTokenizer
except ImportError:
    ctranslate2 = None
    AutoTokenizer = None

from ..base import BaseTranslator

# ISO 639-1 코드를 NLLB 언어 코드로 매핑
NLLB_LANG_CODES = {
    "en": "eng_Latn",
    "ko": "kor_Hang",
    "ja": "jpn_Jpan",
    "zh": "zho_Hans",
    "zh-TW": "zho_Hant",
    "fr": "fra_Latn",
    "de": "deu_Latn",
    "es": "spa_Latn",
    "it": "ita_Latn",
    "pt": "por_Latn",
    "ru": "rus_Cyrl",
    "ar": "arb_Arab",
    "hi": "hin_Deva",
    "th": "tha_Thai",
    "vi": "vie_Latn",
    "id": "ind_Latn",
    "nl": "nld_Latn",
    "pl": "pol_Latn",
    "tr": "tur_Latn",
    "uk": "ukr_Cyrl",
    "cs": "ces_Latn",
    "sv": "swe_Latn",
    "da": "dan_Latn",
    "fi": "fin_Latn",
    "el": "ell_Grek",
    "he": "heb_Hebr",
    "hu": "hun_Latn",
    "ro": "ron_Latn",
    "bg": "bul_Cyrl",
    "no": "nob_Latn",
}


class NLLBTranslator(BaseTranslator):
    """
    Meta NLLB-200 다국어 번역기입니다.
    CTranslate2 최적화 버전을 사용하여 빠른 추론을 제공합니다.
    
    지원 언어: 200개 언어 (한국어, 영어, 일본어, 중국어 등)
    """

    def __init__(self):
        """
        NLLBTranslator를 초기화합니다.
        CTranslate2 모델과 토크나이저를 로드합니다.
        """
        if ctranslate2 is None or AutoTokenizer is None:
            raise ImportError(
                "ctranslate2 또는 transformers가 설치되지 않았습니다. "
                "`pip install ctranslate2 transformers sentencepiece`을 실행해주세요."
            )
        
        print("NLLB-200 모델을 로드하는 중입니다 (CTranslate2 최적화 버전)...")
        
        # CTranslate2 최적화 모델 (int8 양자화, 약 600MB)
        self.ct2_model_id = "JustFrederik/nllb-200-distilled-600M-ct2-int8"
        self.tokenizer_id = "facebook/nllb-200-distilled-600M"
        
        # 토크나이저 로드 (작은 파일들만 받으므로 빠름)
        self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_id)
        
        # CTranslate2 모델 다운로드 및 로드
        try:
            from huggingface_hub import snapshot_download
            model_path = snapshot_download(repo_id=self.ct2_model_id)
            self.translator = ctranslate2.Translator(model_path, device="auto")
        except Exception as e:
            raise RuntimeError(f"NLLB 모델 로드 실패: {e}")
        
        print("NLLB-200 모델 로드 완료 (CTranslate2).")

    def _get_nllb_code(self, lang_code: str) -> str:
        """ISO 639-1 언어 코드를 NLLB 언어 코드로 변환합니다."""
        return NLLB_LANG_CODES.get(lang_code, "eng_Latn")

    def translate_batch(self, sentences, src, dest, max_workers=1, progress_cb=None):
        """여러 문장을 순차적으로 번역합니다."""
        results = []
        total = len(sentences)
        
        print(f"NLLB: Starting translation of {total} items...")
        
        for i, text in enumerate(sentences):
            try:
                translated = self.translate(text, src, dest)
                results.append(translated)
            except Exception as e:
                print(f"NLLB batch processing error at index {i}: {e}")
                results.append(text)
            
            if progress_cb:
                progress_cb((i + 1) / total, f"({i + 1}/{total})")
                
        return results

    def translate(self, text: str, src: str, dest: str) -> str:
        """
        NLLB-200 모델을 사용하여 텍스트를 번역합니다.
        """
        if not text or not text.strip():
            return text
        
        src_lang = self._get_nllb_code(src)
        tgt_lang = self._get_nllb_code(dest)
        
        try:
            # 소스 언어 설정
            self.tokenizer.src_lang = src_lang
            
            # 토큰화
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            input_tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
            
            # CTranslate2로 번역
            results = self.translator.translate_batch(
                [input_tokens],
                target_prefix=[[tgt_lang]],
                beam_size=4,
                max_decoding_length=512
            )
            
            # 결과 디코딩
            output_tokens = results[0].hypotheses[0]
            # 타겟 언어 토큰 제거
            if output_tokens and output_tokens[0] == tgt_lang:
                output_tokens = output_tokens[1:]
            
            translated_text = self.tokenizer.decode(
                self.tokenizer.convert_tokens_to_ids(output_tokens),
                skip_special_tokens=True
            )
            
            return translated_text.strip()
            
        except Exception as e:
            print(f"NLLB translation error: {e}")
            return text

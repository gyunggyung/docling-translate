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

    def translate_batch(self, sentences, src, dest, max_workers=1, progress_cb=None, chunk_size=16):
        """
        CTranslate2의 진정한 배치 처리를 활용하여 여러 문장을 효율적으로 번역합니다.
        
        Args:
            sentences: 번역할 문장 리스트
            src: 원본 언어 코드
            dest: 대상 언어 코드
            max_workers: (미사용) 호환성을 위해 유지
            progress_cb: 진행률 콜백 함수
            chunk_size: 한 번에 배치 처리할 문장 수 (기본값: 16, NLLB는 더 큰 배치 가능)
        
        Returns:
            번역된 문장 리스트 (입력과 동일한 순서 보장)
        """
        results = []
        total = len(sentences)
        
        src_lang = self._get_nllb_code(src)
        tgt_lang = self._get_nllb_code(dest)
        self.tokenizer.src_lang = src_lang
        
        # 청크 단위로 분할
        chunks = [sentences[i:i + chunk_size] for i in range(0, total, chunk_size)]
        
        print(f"NLLB: CTranslate2 배치 번역 시작 ({total}개 문장 → {len(chunks)}개 청크, 청크 크기: {chunk_size})")
        
        processed_count = 0
        for i, chunk in enumerate(chunks):
            try:
                # 배치 토큰화
                all_input_tokens = []
                for text in chunk:
                    if not text or not text.strip():
                        all_input_tokens.append([])  # 빈 문장 처리
                    else:
                        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
                        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
                        all_input_tokens.append(tokens)
                
                # 빈 문장 필터링 및 결과 위치 추적
                non_empty_indices = [j for j, tokens in enumerate(all_input_tokens) if tokens]
                non_empty_tokens = [all_input_tokens[j] for j in non_empty_indices]
                
                if non_empty_tokens:
                    # CTranslate2 배치 번역 (진정한 배치 처리)
                    batch_results = self.translator.translate_batch(
                        non_empty_tokens,
                        target_prefix=[[tgt_lang]] * len(non_empty_tokens),
                        beam_size=4,
                        max_decoding_length=512,
                        repetition_penalty=1.2  # 반복 토큰 생성 억제
                    )
                    
                    # 결과 디코딩
                    translated_texts = []
                    for result in batch_results:
                        output_tokens = result.hypotheses[0]
                        # 타겟 언어 토큰 제거
                        if output_tokens and output_tokens[0] == tgt_lang:
                            output_tokens = output_tokens[1:]
                        
                        translated_text = self.tokenizer.decode(
                            self.tokenizer.convert_tokens_to_ids(output_tokens),
                            skip_special_tokens=True
                        )
                        translated_texts.append(translated_text.strip())
                else:
                    translated_texts = []
                
                # 원래 순서대로 결과 재조합 (빈 문장은 원문 유지)
                chunk_results = []
                translated_idx = 0
                for j in range(len(chunk)):
                    if j in non_empty_indices:
                        chunk_results.append(translated_texts[translated_idx])
                        translated_idx += 1
                    else:
                        chunk_results.append(chunk[j])  # 빈 문장은 원문 유지
                
                results.extend(chunk_results)
                
            except Exception as e:
                # Fallback: 개별 번역
                print(f"NLLB 배치 처리 오류 (청크 {i+1}): {e}")
                for text in chunk:
                    try:
                        results.append(self.translate(text, src, dest))
                    except Exception as inner_e:
                        print(f"개별 번역 실패: {inner_e}")
                        results.append(text)
            
            # 진행률 업데이트
            processed_count += len(chunk)
            if progress_cb:
                progress_cb(processed_count / total, f"({processed_count}/{total})")
        
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
                max_decoding_length=512,
                repetition_penalty=1.2  # 반복 토큰 생성 억제
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

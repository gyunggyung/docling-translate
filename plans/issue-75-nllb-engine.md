# Issue #75: NLLB-200 번역 엔진 추가

## 목표

Meta의 `facebook/nllb-200-distilled-600M` 모델을 사용하는 다국어 번역 엔진을 추가합니다.

## 배경

- **모델**: [facebook/nllb-200-distilled-600M](https://huggingface.co/facebook/nllb-200-distilled-600M)
- **크기**: 600M 파라미터 (약 2.4GB)
- **특징**: 200개 언어 지원, 인코더-디코더 구조 (Transformer)
- **라이선스**: CC-BY-NC
- **기술**: HuggingFace Transformers 기반 (GGUF 미지원)

> [!IMPORTANT]
> 이 엔진은 **200개 언어**를 지원하며, 기존 로컬 모델(LFM2, Qwen)과 달리 transformers 라이브러리 사용.

## 제안 변경 사항

### 번역 엔진 모듈

#### [NEW] [nllb.py](file:///c:/github/docling-translate/src/translation/engines/nllb.py)

**목적**: NLLB-200 다국어 번역 엔진

**주요 기능**:
- `NLLBTranslator` 클래스 (BaseTranslator 상속)
- AutoTokenizer, AutoModelForSeq2SeqLM 사용
- 200개 언어 코드 매핑 (ISO 639 → NLLB 코드)

**핵심 구현**:
```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

class NLLBTranslator(BaseTranslator):
    def __init__(self):
        self.model_id = "facebook/nllb-200-distilled-600M"
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
    
    def translate(self, text: str, src: str, dest: str) -> str:
        # ISO 639 코드를 NLLB 언어 코드로 변환 (예: 'ko' -> 'kor_Hang')
        src_lang = LANG_CODE_MAP.get(src, "eng_Latn")
        tgt_lang = LANG_CODE_MAP.get(dest, "kor_Hang")
        
        translator = pipeline("translation", model=self.model, tokenizer=self.tokenizer,
                              src_lang=src_lang, tgt_lang=tgt_lang)
        result = translator(text)
        return result[0]['translation_text']
```

---

### 엔진 등록

#### [MODIFY] [__init__.py](file:///c:/github/docling-translate/src/translation/__init__.py)

- `NLLBTranslator` import 추가
- engines 딕셔너리에 `"nllb"` 키 등록

---

### UI/CLI 반영

#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)

- 엔진 선택 목록에 `"nllb"` 추가
- 워커 기본값 1 조건에 `"nllb"` 추가

#### [MODIFY] [main.py](file:///c:/github/docling-translate/main.py)

- `--engine` choices에 `"nllb"` 추가
- 워커 기본값 조정 조건에 추가

---

### 문서 업데이트

#### [MODIFY] README.md, docs/README.en.md, docs/USAGE.md

- 엔진 목록에 NLLB 추가
- 사용 예시 추가

---

## 검증 계획

### 수동 테스트

사용자가 직접 테스트 진행 (이전 작업과 동일한 방식)

---

## 예상 효과

- **다국어 지원**: 200개 언어 지원으로 범용성 확대
- **로컬 실행**: API 키 없이 무료 사용
- **품질**: 번역 전용 모델로 일반 LLM보다 높은 번역 품질

---

## 주의사항

- `transformers`, `torch`, `sentencepiece` 패키지 필요
- 첫 실행 시 모델 다운로드 (약 2.4GB)
- GPU 없이도 동작하나 속도가 느릴 수 있음

---

*계획 작성일: 2026-01-01*

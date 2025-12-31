# Issue #93: LFM2-1.2B-KOEN-MT 번역 엔진 추가

## 목표

`gyung/lfm2-1.2b-koen-mt-v8-rl-10k-merged-GGUF` 모델을 사용하는 한국어-영어 전용 번역 엔진을 추가합니다.

## 배경

- **모델**: [gyung/lfm2-1.2b-koen-mt-v8-rl-10k-merged-GGUF](https://huggingface.co/gyung/lfm2-1.2b-koen-mt-v8-rl-10k-merged-GGUF)
- **양자화**: Q5_K_M (843MB)
- **특징**: 한국어 ↔ 영어 번역 전용으로 Fine-tuning된 모델
- **참고 코드**: 기존 `lfm2.py` 엔진

> [!IMPORTANT]
> 이 엔진은 다른 엔진과 달리 **한국어/영어만 지원**합니다.
> - 한국어 원문 → 영어 번역
> - 영어 원문 → 한국어 번역

## 제안 변경 사항

### 번역 엔진 모듈

#### [NEW] [lfm2_koen.py](file:///c:/github/docling-translate/src/translation/engines/lfm2_koen.py)

**목적**: 한국어-영어 전용 번역 엔진

**주요 기능**:
- `LFM2KOENTranslator` 클래스 (BaseTranslator 상속)
- Q5_K_M 모델 자동 다운로드 및 로드
- 간소화된 프롬프트 형식:
  ```
  if direction == "en2ko": 
      system = "Translate the following text to Korean."
  else: 
      system = "Translate the following text to English."
  ```
- 순차 처리 방식 (`translate_batch` 오버라이드)

**핵심 구현**:
```python
class LFM2KOENTranslator(BaseTranslator):
    """
    한국어-영어 전용 번역기 (gyung/lfm2-1.2b-koen-mt-v8-rl-10k-merged-GGUF)
    """
    
    # 지원 언어 제한 (한국어/영어만)
    SUPPORTED_LANGUAGES = {'ko', 'en'}
    
    def __init__(self):
        # Q5_K_M 모델 다운로드 및 로드
        self.model_path = hf_hub_download(
            repo_id="gyung/lfm2-1.2b-koen-mt-v8-rl-10k-merged-GGUF",
            filename="lfm2-1.2b-koen-mt-v8-rl-10k-merged-Q5_K_M.gguf"
        )
        self.llm = Llama(model_path=self.model_path, n_ctx=4096, verbose=False)
    
    def translate(self, text: str, src: str, dest: str) -> str:
        # 간소화된 프롬프트 사용
        if dest == "ko":
            system = "Translate the following text to Korean."
        else:
            system = "Translate the following text to English."
        
        prompt = f"<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{text}<|im_end|>\n<|im_start|>assistant\n"
        # ...
```

---

## 검증 계획

### 1. 수동 테스트

**시나리오 1: 영어 → 한국어 번역**
- 단계:
  1. `app.py` 실행 (`python -m src.app`)
  2. 번역 엔진에서 "LFM2-1.2B-KOEN-MT" 선택
  3. `samples/1706.03762v7.pdf` 업로드
  4. 원본 언어: English, 대상 언어: Korean 선택
  5. 번역 실행
- 예상 결과: 한국어로 번역된 결과 출력

**시나리오 2: 한국어 → 영어 번역**
- 단계:
  1. 한국어 텍스트가 포함된 PDF 업로드
  2. 원본 언어: Korean, 대상 언어: English 선택
  3. 번역 실행
- 예상 결과: 영어로 번역된 결과 출력

### 2. 검증 체크리스트

- [ ] 모델 다운로드 정상 동작
- [ ] 영어 → 한국어 번역 정상 동작
- [ ] 한국어 → 영어 번역 정상 동작
- [ ] 표준 샘플(`samples/1706.03762v7.pdf`)로 테스트
- [ ] 기존 기능이 정상 동작하는지 확인

---

## 예상 효과

- **품질**: GRPO 학습을 통해 일반 LFM2보다 향상된 한영/영한 번역 품질
- **크기**: Q5_K_M (843MB)로 적절한 품질/크기 균형
- **성능**: 전용 모델로 한-영 번역에 최적화된 결과

---

## 주의사항

- 이 엔진은 **한국어/영어만 지원**하므로 다른 언어 선택 시 에러 처리 필요
- 모델 처음 로드 시 Hugging Face에서 843MB 다운로드 필요
- llama-cpp-python 및 huggingface_hub 패키지 필요

---

*계획 작성일: 2026-01-01*

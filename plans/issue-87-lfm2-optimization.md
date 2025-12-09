# Issue #87: LFM2-1.2B 모델 번역 프롬프트 단순화 및 생성 파라미터 최적화

## 목표

LFM2-1.2B 모델(소형 모델)의 특성에 맞춰 프롬프트를 단순화하고 생성 파라미터를 최적화하여 번역 품질의 일관성과 성능을 개선합니다.

## 배경

현재 LFM2Translator는 XML 태그(`<src>`, `<tgt>`)와 Assistant Pre-fill을 사용하는 복잡한 구조를 가지고 있어, 1.2B 규모의 모델이 혼란스러워하거나 성능이 저하되는 문제가 있습니다. LiquidAI 및 커뮤니티 피드백에 따라 이를 단순 자연어 지시로 변경하고 모델 카드의 권장 파라미터를 적용해야 합니다.

## 제안 변경 사항

### Translation Engine

#### [MODIFY] [src/translation/engines/lfm2.py](file:///c:/github/docling-translate/src/translation/engines/lfm2.py)

**변경 내용**:

1.  **Llama 인스턴스 초기화 변경**:
    -   `n_ctx`를 2048에서 4096으로 증가시켜 더 긴 문맥 처리를 지원합니다.

2.  **프롬프트 구조 변경**:
    -   `<src>`, `<tgt>` 태그 제거.
    -   표준 ChatML 포맷의 자연어 지시문으로 변경.
    -   "Output ONLY the translated text" 지시 강화.

3.  **생성 파라미터 최적화**:
    -   `temperature`: 0.1 → 0.3 (약간의 창의성 허용하여 유창성 개선)
    -   `top_p` 제거 및 `min_p`: 0.15 추가 (모델 권장사항)
    -   `repetition_penalty`: 1.05 추가 (반복 생성 방지)
    -   `stop` 토큰에서 `</tgt>` 제거.

4.  **후처리 로직 간소화**:
    -   태그 제거를 위한 Regex 코드 삭제.
    -   따옴표 제거 로직은 유지.

**핵심 코드**:
```python
# 변경 전 (__init__)
self.llm = Llama(
    model_path=self.model_path,
    n_ctx=2048,
    verbose=False
)

# 변경 후 (__init__)
self.llm = Llama(
    model_path=self.model_path,
    n_ctx=4096, # Context Window 확장
    verbose=False
)

# 변경 전 (translate)
prompt = f"""<|im_start|>system
You are a professional translator. Translate the text from {src_name} to {dest_name}.
Output ONLY the translated text inside <tgt> tags. Do not interpret the text, just translate it.
<|im_end|>
<|im_start|>user
<src>{text}</src><|im_end|>
<|im_start|>assistant
<tgt>"""

# 변경 후 (translate)
prompt = f"""<|im_start|>system
You are a professional translator. Translate the following text from {src_name} to {dest_name}.
Output ONLY the translated text. Do not provide any explanations or notes.
<|im_end|>
<|im_start|>user
{text}<|im_end|>
<|im_start|>assistant
"""

# 변경 전 (generation)
output = self.llm(
    prompt,
    max_tokens=512,
    stop=["</tgt>", "<|im_end|>"],
    temperature=0.1,
    top_p=0.9,
    echo=False
)

# 변경 후 (generation)
output = self.llm(
    prompt,
    max_tokens=512,
    stop=["<|im_end|>"],
    temperature=0.3,
    min_p=0.15, # Top-p 대신 min_p 사용
    repetition_penalty=1.05,
    echo=False
)
```

---

## 검증 계획

### 수동 테스트

**시나리오 1: 표준 샘플 번역 테스트**
- 단계:
  1. `main.py`를 사용하여 `samples/1706.03762v7.pdf`를 한국어로 번역 (LFM2 엔진 사용).
     ```powershell
     python main.py samples/1706.03762v7.pdf --engine lfm2 --source en --target ko
     ```
  2. 생성된 HTML 파일을 열어 번역 품질 확인.
- 예상 결과:
  - 번역이 XML 태그 없이 깔끔하게 출력되어야 함.
  - 불필요한 설명(Here is the translation... 등)이 없어야 함.
  - 문맥이 자연스럽게 연결되어야 함.

### 검증 체크리스트

- [ ] `LFM2Translator`가 오류 없이 초기화되는지 확인 (`n_ctx` 변경 영향).
- [ ] 번역 결과에 `<tgt>` 같은 태그가 남아있지 않은지 확인.
- [ ] 반복 생성(repetition)이 발생하지 않는지 확인.

---

## 예상 효과

- **품질**: 1.2B 모델에 최적화된 프롬프트를 사용하여 번역의 정확도와 자연스러움 향상.
- **성능**: 불필요한 태그 생성 및 처리 과정을 줄여 약간의 효율성 개선 가능.

## 주의사항

- `llama-cpp-python` 버전이 `min_p` 파라미터를 지원해야 함 (최신 버전 권장).

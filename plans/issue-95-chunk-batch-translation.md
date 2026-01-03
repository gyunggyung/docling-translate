# Issue #95: 청크(Chunk) 단위 배치 번역 (All Local Engines)

## 목표

모든 로컬 번역 엔진의 속도를 개선하기 위해 배치(Batch) 처리 기능을 구현합니다.
특히 **1:1 문장 매핑의 정확성**을 최우선으로 고려하며, 매핑 실패 시 개별 번역으로 폴백(Fallback)하는 안전장치를 마련합니다.

## 배경

기존 로컬 엔진들은 `translate_batch` 메서드에서 문장을 하나씩 순차 처리(`for` loop)하고 있어, LLM의 컨텍스트 스위칭 오버헤드나 CTranslate2의 배치 가속 이점을 살리지 못하고 있습니다. 이를 개선하여 전반적인 번역 성능을 향상시켜야 합니다.

## 현재 코드 상황 분석

### 엔진별 현황

| 엔진 파일 | translate_batch 구현 | 현재 방식 |
|-----------|---------------------|-----------|
| `lfm2.py` | ✅ 자체 구현 | 순차 for 루프 |
| `lfm2_koen.py` | ✅ 자체 구현 | 순차 for 루프 |
| `qwen.py` | ❌ BaseTranslator 상속 | 순차 for 루프 |
| `yanolja.py` | ❌ BaseTranslator 상속 | 순차 for 루프 |
| `nllb.py` | ✅ 자체 구현 | 순차 for 루프 (CT2 배치 미활용) |
| `nllb_koen.py` | ✅ 자체 구현 | 순차 for 루프 (CT2 배치 미활용) |

> **참고**: `qwen.py`와 `yanolja.py`는 `translate_batch`를 오버라이드하지 않아 `BaseTranslator`의 기본 구현을 사용합니다.

---

## 제안 변경 사항

### 1. LLM 기반 엔진 (LFM2, LFM2_KOEN, Qwen, Yanolja)

**대상 파일**:
- `src/translation/engines/lfm2.py`
- `src/translation/engines/lfm2_koen.py`
- `src/translation/engines/qwen.py` (신규 추가 필요)
- `src/translation/engines/yanolja.py` (신규 추가 필요)

**변경 전략**:
- **Tagging 방식**: 여러 문장을 `<sN>문장</sN>` 형태로 묶어 하나의 프롬프트로 전송합니다.
- **System Prompt 조정**: 모델이 태그 구조를 유지한 채 번역하도록 지시문을 보강합니다.
- **Safety Mechanism (중요)**:
    - 번역 결과에서 태그 파싱 수행.
    - 입력된 문장 수와 출력된 문장 수가 일치하지 않거나 태그가 깨진 경우, **해당 청크의 문장들을 하나씩 개별 번역(Serial Translation)**하도록 Fallback 합니다.
- **Chunk Size**: 기본값 5 (안정성 고려).

**핵심 코드 (공통 패턴)**:
```python
import re

def translate_batch(self, sentences, src, dest, max_workers=1, progress_cb=None, chunk_size=5):
    """청크 단위 배치 번역을 수행합니다."""
    results = []
    total = len(sentences)
    chunks = [sentences[i:i + chunk_size] for i in range(0, total, chunk_size)]
    
    for i, chunk in enumerate(chunks):
        # 1. 청크 번역 시도
        try:
            chunk_results = self._translate_chunk(chunk, src, dest)
            
            # 검증: 개수가 맞고 빈 칸이 너무 많지 않은지 확인
            if len(chunk_results) != len(chunk) or chunk_results.count("") > len(chunk) // 2:
                raise ValueError("Chunk parsing failed or quality low")
                
            results.extend(chunk_results)
            
        except Exception as e:
            # 2. 실패 시 문장별 순차 번역 (Fallback)
            print(f"Batch failed, falling back to serial: {e}")
            for text in chunk:
                results.append(self.translate(text, src, dest))
        
        # 진행률 업데이트
        if progress_cb:
            current_count = min((i + 1) * chunk_size, total)
            progress_cb(current_count / total, f"({current_count}/{total})")
            
    return results

def _translate_chunk(self, chunk: list, src: str, dest: str) -> list:
    """청크를 태그로 묶어 번역하고 파싱합니다."""
    # 태그로 묶기
    combined_text = "\n".join([f"<s{j}>{text}</s{j}>" for j, text in enumerate(chunk)])
    
    # 청크 번역용 프롬프트 (모델별 조정 필요)
    # LFM2-KOEN의 경우:
    if dest == "ko":
        system = "Translate each tagged sentence to Korean. Keep the <sN></sN> tags intact."
    else:
        system = "Translate each tagged sentence to English. Keep the <sN></sN> tags intact."
    
    prompt = f"""<|im_start|>system
{system}<|im_end|>
<|im_start|>user
{combined_text}<|im_end|>
<|im_start|>assistant
"""
    
    # 모델 호출 (기존 translate 로직 활용)
    output = self.llm(
        prompt,
        max_tokens=512 * len(chunk),  # 청크 크기에 비례
        stop=["<|im_end|>"],
        temperature=0.3,
        min_p=0.15,
        repeat_penalty=1.05,
        echo=False
    )
    
    translated_combined = output['choices'][0]['text'].strip()
    
    # 파싱
    return self._parse_chunk_result(translated_combined, len(chunk))

def _parse_chunk_result(self, text: str, expected_count: int) -> list:
    """태그로 묶인 번역 결과를 파싱합니다."""
    parsed = []
    for j in range(expected_count):
        # 태그 파싱 (<s0>...</s0>)
        pattern = f"<s{j}>(.*?)</s{j}>"
        match = re.search(pattern, text, re.DOTALL)
        parsed.append(match.group(1).strip() if match else "")
    return parsed
```

### 2. NLLB 기반 엔진 (NLLB, NLLB_KOEN)

**대상 파일**:
- `src/translation/engines/nllb.py`
- `src/translation/engines/nllb_koen.py`

**현재 문제점**:
- 현재 코드에서 `translator.translate_batch([input_tokens], ...)`를 호출하지만, **단일 문장 리스트**만 전달하여 배치 효과가 없음.

**변경 전략**:
- 기존의 수동 루프를 제거하고, **여러 문장의 토큰 리스트**를 한 번에 `translator.translate_batch`에 전달합니다.
- 토크나이징 및 디코딩 과정도 배치 처리에 맞춰 수정합니다.

**핵심 코드 변경**:
```python
def translate_batch(self, sentences, src, dest, max_workers=1, progress_cb=None, chunk_size=16):
    """CTranslate2의 진정한 배치 처리를 활용합니다."""
    results = []
    total = len(sentences)
    
    src_lang = self._get_nllb_code(src)
    tgt_lang = self._get_nllb_code(dest)
    self.tokenizer.src_lang = src_lang
    
    # 청크 단위로 처리
    chunks = [sentences[i:i + chunk_size] for i in range(0, total, chunk_size)]
    
    for i, chunk in enumerate(chunks):
        try:
            # 배치 토큰화
            all_input_tokens = []
            for text in chunk:
                inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
                tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
                all_input_tokens.append(tokens)
            
            # CTranslate2 배치 번역
            batch_results = self.translator.translate_batch(
                all_input_tokens,
                target_prefix=[[tgt_lang]] * len(chunk),
                beam_size=4,
                max_decoding_length=512
            )
            
            # 배치 디코딩
            for result in batch_results:
                output_tokens = result.hypotheses[0]
                if output_tokens and output_tokens[0] == tgt_lang:
                    output_tokens = output_tokens[1:]
                
                translated_text = self.tokenizer.decode(
                    self.tokenizer.convert_tokens_to_ids(output_tokens),
                    skip_special_tokens=True
                )
                results.append(translated_text.strip())
                
        except Exception as e:
            print(f"NLLB batch processing error: {e}")
            # Fallback: 개별 번역
            for text in chunk:
                results.append(self.translate(text, src, dest))
        
        # 진행률 업데이트
        if progress_cb:
            current_count = min((i + 1) * chunk_size, total)
            progress_cb(current_count / total, f"({current_count}/{total})")
    
    return results
```

---

## 검증 계획

### 테스트 환경
- **테스트 대상**: `lfm2-koen` 엔진 **단독** (우선 적용)
- **테스트 파일**: `samples/1706.03762v7-8.pdf`
- **OS**: Windows 11

### 시간 측정 방법

현재 `main.py`에 `--benchmark` 옵션이 **문서에만 있고 실제 구현되지 않음**.
따라서 **수동 시간 측정**을 사용합니다:

```bash
# Windows PowerShell에서 실행
Measure-Command { python main.py samples/1706.03762v7-8.pdf --engine lfm2-koen-mt } | Select-Object TotalSeconds
```

또는 출력 로그에서 `일괄 번역 완료 (xx.xx초)` 메시지를 확인합니다.

### 1. Baseline 측정
- 변경 전 상태에서 `main.py` 실행 (엔진: `lfm2-koen-mt`).
- 번역 소요 시간 기록.

### 2. 구현 및 적용
- `lfm2_koen.py` 수정 (우선 적용 및 테스트).
- (승인 후 나머지 파일들도 동일 패턴 적용).

### 3. Optimization 측정
- 변경 후 상태에서 동일 테스트 실행.
- 번역 소요 시간 측정 및 비교.
- **1:1 매핑 검증**: 생성된 HTML 파일을 열어 문장 밀림 현상이 없는지 육안 확인.

### 4. 확장
- `lfm2-koen` 검증 완료 시, 다른 LLM 엔진(`lfm2`, `qwen`, `yanolja`) 및 NLLB 엔진들에 코드 적용.

---

## 구현 우선순위

1. **Phase 1**: `lfm2_koen.py` 수정 및 검증
2. **Phase 2**: `lfm2.py` 동일 패턴 적용
3. **Phase 3**: `qwen.py`, `yanolja.py` `translate_batch` 오버라이드 추가
4. **Phase 4**: `nllb.py`, `nllb_koen.py` CTranslate2 배치 최적화

---

## 주의사항

- **프롬프트 오염 방지**: LLM이 번역문에 태그를 누락하거나 환각을 일으킬 수 있습니다. Fallback 로직이 필수적입니다.
- **메모리 사용량**: 배치 크기가 커지면 컨텍스트 길이가 늘어나 메모리 부족(OOM)이 발생할 수 있으므로, 적절한 `chunk_size`(5~10) 유지가 필요합니다.
- **NLLB 특수성**: CTranslate2는 진정한 배치 처리를 지원하므로, `chunk_size`를 16~32로 더 크게 설정 가능합니다.

---

## 예상 효과

- LLM 엔진: 문장 수 N에서 약 N/chunk_size 배 속도 향상 기대 (컨텍스트 스위칭 감소)
- NLLB 엔진: CTranslate2 배치 가속으로 2~5배 속도 향상 기대

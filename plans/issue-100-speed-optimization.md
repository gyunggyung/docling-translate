# Issue #100: 속도 최적화 - 상용 서비스 수준의 성능 달성

## 목표

**일반적인 노트북 CPU 환경에서도 Gemini, ChatGPT, Claude와 비견할 수 있는 문서 번역 속도를 달성하는 것**이 목표입니다. 현재 시스템의 병목점을 분석하고, 단계별 최적화를 통해 실용적인 속도를 확보합니다.

## 배경

### 현재 문제점

`docling-translate`는 **편리성**과 **보안**(로컬 실행)을 제공하지만, 속도 면에서 상용 서비스에 크게 뒤처집니다:

| 상용 서비스 | 평균 응답 시간 (500단어) | 특징 |
|------------|-------------------------|------|
| Gemini 2.0 Flash | ~6초 | 극저지연, 302 tokens/s |
| ChatGPT 4o mini | ~12초 | 경량화 모델 |
| Claude 3.5 Sonnet | ~4초 | 일관된 저지연 |

**현재 `docling-translate`의 병목점:**

1. **Docling 변환 (약 60-70%)**: PDF 레이아웃 분석, 테이블 구조 인식에 상당한 시간 소요
   - CPU에서 약 1.74초/페이지 (GPU 사용 시 0.49초)
   - 15페이지 PDF → 약 26-30초
   
2. **로컬 LLM 번역 (약 30%)**: llama.cpp 기반 추론
   - 1.2B 모델, Q5_K_M 양자화에서도 CPU 추론 느림
   - 문장당 1-2초 예상 → 200문장 기준 200-400초

3. **기타 (약 5-10%)**: HTML 생성, 이미지 저장 등

### 참고 자료

- [Docling 공식 문서](https://docling-project.github.io/docling/)
- [Docling GitHub](https://github.com/docling-project/docling)
- Issue #92: 기존 CPU 병렬 처리 최적화 (OMP_NUM_THREADS 설정)

---

## 분석: 속도 최적화 전략

### 1. Docling 최적화 (문서 변환 단계)

#### 1.1 PDF 백엔드 최적화

| 백엔드 | 속도 | 품질 | 권장 상황 |
|--------|------|------|----------|
| `docling-parse-v2` | 보통 | 높음 | 기본값, 복잡한 레이아웃 |
| `pypdfium2` | **매우 빠름** | 중간 | **디지털 PDF 추천** |
| `docling-parse-v4` | 느림 | 최고 | OCR 필요 시 |

**핵심**: 디지털 PDF(스캔 아닌 원본 PDF)의 경우 `pypdfium2` 백엔드 사용으로 **3-5배 속도 향상** 가능

#### 1.2 선택적 기능 비활성화

```python
# 현재 설정 (정밀도 우선)
pipeline_options.do_table_structure = True
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

# 최적화 설정 (속도 우선)
pipeline_options.do_table_structure = True
pipeline_options.table_structure_options.mode = TableFormerMode.FAST  # 40% 빠름
pipeline_options.do_ocr = False  # OCR 비활성화 (디지털 PDF 시)
pipeline_options.generate_picture_images = False  # 필요 없으면 비활성화
```

#### 1.3 스레드 수 최적화

현재 `multiprocessing.cpu_count()` (논리 코어) 사용 중이나, Docling은 **물리 코어 수**가 더 효율적일 수 있음:

```python
# 권장: 물리 코어 수 사용
physical_cores = os.cpu_count() // 2
os.environ["OMP_NUM_THREADS"] = str(physical_cores)
```

#### 1.4 AcceleratorOptions 활용

```python
from docling.datamodel.pipeline_options import AcceleratorOptions, AcceleratorDevice

# CPU 최적화 설정
accelerator_options = AcceleratorOptions(
    device=AcceleratorDevice.CPU,
    num_threads=physical_cores
)
pipeline_options.accelerator_options = accelerator_options
```

---

### 2. 로컬 LLM 최적화 (번역 단계)

#### 2.1 현재 상태 분석

**현재 코드 (`lfm2_koen.py`)**:
- 모델: `gyung/lfm2-1.2b-koen-mt-v8-rl-10k-merged-GGUF` (Q5_K_M, 843MB)
- 설정: `n_ctx=4096`, `n_threads=physical_cores`
- 처리: 순차 번역 (병렬 처리 없음)

**문제점**:
1. **순차 처리 병목**: 200문장 → 200번의 개별 inference 호출
2. **Q5_K_M 양자화**: 품질 좋으나 Q4보다 느림
3. **긴 컨텍스트**: `n_ctx=4096`은 번역에 과도함

#### 2.2 최적화 전략

| 전략 | 예상 효과 | 구현 난이도 |
|------|----------|-------------|
| **배치 프롬프트 (Batch Prompting)** | 2-3배 ↑ | 중간 |
| **Q4_K_M 양자화 사용** | 10-20% ↑ | 쉬움 |
| **컨텍스트 크기 축소** | 5-10% ↑ | 쉬움 |
| **Speculative Decoding** | 1.5-3배 ↑ | 어려움 |
| **Flash Attention** | 10-30% ↑ | 중간 |

##### 2.2.1 배치 프롬프트 (가장 효과적)

현재 문장별 개별 호출 대신, 여러 문장을 하나의 프롬프트로 묶어 처리:

```python
# Before (현재): 문장별 개별 호출
for sentence in sentences:
    translate(sentence)  # 200번 호출

# After (최적화): 배치 프롬프트
batch_prompt = """Translate the following texts to Korean. Return each translation on a new line.

1. {sentence1}
2. {sentence2}
3. {sentence3}
..."""
# 1번 호출로 여러 문장 처리
```

**주의사항**:
- 배치 크기는 컨텍스트 제한 내에서 조정 (5-10문장 권장)
- 출력 파싱 로직 필요

##### 2.2.2 Q4_K_M 양자화 전환

```python
# Q5_K_M (현재, 843MB) → Q4_K_M (더 빠름, ~600MB)
# 품질 저하 미미, 속도 10-20% 향상
filename="lfm2-1.2b-koen-mt-v8-rl-10k-merged-Q4_K_M.gguf"
```

##### 2.2.3 컨텍스트 크기 최적화

```python
# 번역 작업에 4096 토큰은 과도함
# 512-1024 토큰이면 충분
self.llm = Llama(
    model_path=self.model_path,
    n_ctx=1024,  # 4096 → 1024 (메모리 & 속도 개선)
    n_threads=physical_cores,
)
```

##### 2.2.4 Speculative Decoding (고급)

작은 드래프트 모델로 토큰을 미리 예측하고, 메인 모델이 검증하는 방식:

```bash
# llama.cpp 서버 실행 예시
./llama-server -m main_model.gguf -md draft_model.gguf --draft-max 16
```

CPU 환경에서 **1.5-3배 속도 향상** 가능, 그러나 구현 복잡

---

### 3. 아키텍처 수준 최적화

#### 3.1 API 기반 번역 엔진 우선 권장

**현실적인 조언**: CPU 환경에서 로컬 LLM이 API보다 빨라지기는 어려움

| 엔진 | 예상 속도 | 비용 | 보안 |
|------|----------|------|------|
| Google Translate | 매우 빠름 | 무료(제한)/유료 | 외부 전송 |
| Gemini API | 빠름 | 저렴 | 외부 전송 |
| 로컬 LLM | 느림 | 무료 | **완전 로컬** |

**권장사항**: "빠른 번역" 모드와 "보안 번역" 모드 UI 분리

#### 3.2 스트리밍 출력

사용자 체감 속도 개선을 위한 실시간 출력:

```python
# Streamlit 스트리밍 예시
for chunk in translator.translate_stream(text):
    st.write(chunk)
```

#### 3.3 캐싱 시스템

```python
# 번역 결과 캐싱 (동일 문장 재번역 방지)
import hashlib
import shelve

def get_cached_translation(text, engine):
    cache_key = hashlib.md5(f"{text}:{engine}".encode()).hexdigest()
    with shelve.open("translation_cache") as cache:
        return cache.get(cache_key)
```

---

### 4. Docling 대안 검토

#### 4.1 대안 라이브러리 비교

| 라이브러리 | PDF 변환 속도 | 구조 보존 | 권장 상황 |
|------------|--------------|----------|----------|
| **Docling** | 느림 (1.74s/page) | 매우 좋음 | 정밀 분석 필요 시 |
| **PyMuPDF** | 매우 빠름 | 좋음 | 빠른 텍스트 추출 |
| **marker-pdf** | 빠름 | 좋음 | Markdown 변환 |
| **Kreuzberg** | 빠름 | 좋음 | 신흥 대안 |

**결론**: Docling의 구조 보존 품질이 중요하므로 대체보다는 **최적화**에 집중

---

## 제안 변경 사항

> **참고**: 버그 수정 사항(PyTorch+Streamlit 호환성, deprecated API)은 [Issue #102](https://github.com/gyunggyung/docling-translate/issues/102)에서 해결되었습니다.

### Phase 1: 즉시 적용 가능한 최적화 (1-2일)

#### [MODIFY] [core.py](file:///c:/github/docling-translate/src/core.py)

**변경 내용**:
1. `TableFormerMode.FAST` 모드 옵션 추가
2. `pypdfium2` 백엔드 옵션 추가
3. `AcceleratorOptions` 명시적 설정
4. 스피드 모드 프리셋 함수 추가

**핵심 코드**:
```python
from docling.datamodel.pipeline_options import AcceleratorOptions, AcceleratorDevice

def create_converter(speed_mode: str = "balanced") -> DocumentConverter:
    """
    Docling DocumentConverter를 초기화합니다.
    
    Args:
        speed_mode: "fast" | "balanced" | "accurate"
    """
    pipeline_options = PdfPipelineOptions()
    
    # 물리 코어 수 계산
    physical_cores = os.cpu_count() // 2 if os.cpu_count() else 4
    
    # Accelerator 옵션 설정
    pipeline_options.accelerator_options = AcceleratorOptions(
        device=AcceleratorDevice.AUTO,  # 자동 감지 (GPU 있으면 사용)
        num_threads=physical_cores
    )
    
    if speed_mode == "fast":
        pipeline_options.do_ocr = False
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.mode = TableFormerMode.FAST
        pipeline_options.generate_picture_images = False
        pipeline_options.generate_table_images = False
    elif speed_mode == "accurate":
        pipeline_options.do_ocr = False
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        pipeline_options.generate_picture_images = True
        pipeline_options.generate_table_images = True
    else:  # balanced (현재 기본값)
        pipeline_options.do_ocr = False
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        pipeline_options.generate_picture_images = True
        pipeline_options.generate_table_images = True
    
    return DocumentConverter(...)
```

---

#### [MODIFY] [lfm2_koen.py](file:///c:/github/docling-translate/src/translation/engines/lfm2_koen.py)

**변경 내용**:
1. 컨텍스트 크기 축소 (4096 → 1024)
2. 배치 프롬프트 지원 추가
3. Q4_K_M 양자화 옵션 추가

**핵심 코드**:
```python
def __init__(self, quantization: str = "Q5_K_M"):
    """
    Args:
        quantization: "Q4_K_M" (빠름) | "Q5_K_M" (균형) | "Q8_0" (정확)
    """
    self.llm = Llama(
        model_path=self.model_path,
        n_ctx=1024,  # 축소
        n_threads=physical_cores,
        n_batch=512,  # 배치 처리 최적화
        verbose=False
    )

def translate_batch_optimized(self, sentences, src, dest, batch_size=5):
    """배치 프롬프트를 사용한 최적화된 번역"""
    results = []
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i+batch_size]
        batch_prompt = self._create_batch_prompt(batch, dest)
        batch_results = self._translate_batch_prompt(batch_prompt)
        results.extend(batch_results)
    return results
```

---

#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)

**변경 내용**:
1. "속도 모드" 선택 UI 추가 (Fast/Balanced/Accurate)
2. 모드별 예상 속도 표시

---

### Phase 2: 중장기 최적화 (1-2주)

#### [NEW] [src/cache.py](file:///c:/github/docling-translate/src/cache.py)

**목적**: 번역 결과 캐싱으로 재번역 시 속도 향상

**주요 기능**:
- SQLite 기반 번역 캐시
- 해시 기반 중복 탐지
- 자동 만료 (30일)

---

#### [NEW] [src/streaming.py](file:///c:/github/docling-translate/src/streaming.py)

**목적**: 스트리밍 출력으로 체감 속도 개선

**주요 기능**:
- LLM 토큰 스트리밍
- Streamlit 실시간 업데이트

---

## 예상 효과

### 정량적 분석

**테스트 기준**: 15페이지 PDF (1706.03762v7.pdf), 약 200문장

| 단계 | 현재 예상 시간 | 최적화 후 예상 | 개선율 |
|------|---------------|---------------|--------|
| Docling 변환 | ~26초 | ~15초 | 42% ↓ |
| LLM 번역 (200문장) | ~200초 | ~70초 | 65% ↓ |
| HTML 생성 | ~5초 | ~5초 | - |
| **총 시간** | **~231초** | **~90초** | **61% ↓** |

> **주의**: 이 예상치는 이론적 최적화 기준이며, 실제 결과는 하드웨어에 따라 다를 수 있습니다.

### 상용 서비스와의 비교

| 시나리오 | Gemini API | 로컬 최적화 후 | 차이 |
|----------|------------|---------------|------|
| 15페이지 PDF 번역 | ~30초 | ~90초 | 3배 느림 |
| 1페이지 PDF 번역 | ~8초 | ~10초 | **비슷** |
| 짧은 텍스트 (1000자) | ~3초 | ~5초 | 1.7배 느림 |

**결론**: 
- **짧은 문서**: 로컬 LLM도 충분히 경쟁력 있음
- **긴 문서**: API 사용 권장 또는 "보안 모드"임을 명시

---

## 검증 계획

### 1. 벤치마크 테스트

```bash
# 표준 샘플로 성능 측정
python benchmark.py --file samples/1706.03762v7.pdf --mode fast
python benchmark.py --file samples/1706.03762v7.pdf --mode balanced
python benchmark.py --file samples/1706.03762v7.pdf --mode accurate
```

### 2. 수동 테스트 시나리오

**시나리오 1: 속도 모드 비교**
- 단계:
  1. 동일 PDF를 Fast/Balanced/Accurate 모드로 변환
  2. 각 모드의 완료 시간 기록
  3. 결과 품질 육안 확인
- 예상 결과: Fast 모드가 Accurate보다 40% 이상 빠름

**시나리오 2: 배치 프롬프트 효과**
- 단계:
  1. 동일 텍스트를 순차/배치 모드로 번역
  2. 시간 및 품질 비교
- 예상 결과: 배치 모드가 2배 이상 빠름

### 3. 검증 체크리스트

- [ ] Fast 모드가 기존 대비 40% 이상 빠른지 확인
- [ ] Fast 모드에서도 표/이미지가 정상 추출되는지 확인
- [ ] 배치 프롬프트 결과가 개별 번역과 동등한 품질인지 확인
- [ ] 표준 샘플(`samples/1706.03762v7.pdf`)로 전체 테스트
- [ ] 기존 기능(Google, Gemini 엔진 등)이 정상 동작하는지 확인
- [ ] 메모리 사용량이 과도하게 증가하지 않는지 확인

---

## 주의사항

### 품질 트레이드오프

| 최적화 | 속도 향상 | 품질 영향 |
|--------|----------|----------|
| TableFormerMode.FAST | 40% ↑ | 복잡한 표 인식률 소폭 하락 |
| Q4_K_M 양자화 | 15% ↑ | 미미한 번역 품질 저하 |
| 배치 프롬프트 | 200% ↑ | 간혹 파싱 오류 가능 |

### 알려진 제한사항

1. **GPU 없는 환경의 한계**: CPU만으로는 상용 API 수준의 속도 달성 불가능
2. **메모리 사용량**: 배치 처리 시 메모리 사용량 증가 (8GB+ RAM 권장)
3. **로컬 LLM 품질**: Google Translate나 Gemini 대비 번역 품질 열세

### 후속 프로젝트 (안드로이드)

이 최적화 작업은 **안드로이드 환경**에서의 문서 번역 프로젝트의 기초가 됩니다:
- GGUF 모델의 모바일 최적화 (Q4_0, IQ2 등)
- llama.cpp의 Android NDK 빌드
- 경량화된 PDF 파싱 라이브러리 탐색

---

## 구현 우선순위

### 핵심 전략: "속도 모드" 도입

사용자가 **Fast/Balanced** 모드를 선택할 수 있게 하여, 속도와 품질 사이 트레이드오프를 제공합니다.

| 모드 | PDF 백엔드 | TableFormer | n_ctx | 대상 |
|------|-----------|-------------|-------|------|
| **Fast** | pypdfium2 | FAST | 1024 | 속도 우선, 디지털 PDF |
| **Balanced** | docling-parse-v2 | ACCURATE | 4096 | 품질 우선 (기본값) |

### 작업 목록

| 순위 | 작업 | 예상 효과 | 난이도 | 소요 시간 |
|------|------|----------|--------|----------|
| **1** | **속도 모드 UI 추가 (Fast/Balanced)** | 핵심 | 중간 | 2시간 |
| 2 | Fast 모드: pypdfium2 백엔드 | **3-5배 ↑** | 쉬움 | 1시간 |
| 3 | Fast 모드: TableFormerMode.FAST | 40% ↑ | 쉬움 | 30분 |
| 4 | Fast 모드: n_ctx=1024 (Balanced는 4096 유지) | 5-10% ↑ | 쉬움 | 30분 |
| 5 | 배치 프롬프트 구현 | 높음 | 중간 | 1일 (후순위) |
| 6 | 캐싱 시스템 | 중간 | 중간 | 1일 (후순위) |

> **참고**: Q4_K_M 양자화 모델은 이미 GGUF(Q5_K_M)를 사용 중이므로 추가 효과가 미미하여 제외했습니다.

---

### 다음 단계

1. **즉시 구현**: 속도 모드 UI + pypdfium2 + TableFormerMode.FAST + n_ctx 조건부 적용
2. **후순위**: 배치 프롬프트, 캐싱 시스템

---

*계획 작성일: 2026-01-05*
*업데이트: 2026-01-06 (대화 반영)*
*조사 참고 자료: Docling 공식 문서, llama.cpp, Ollama, HuggingFace*

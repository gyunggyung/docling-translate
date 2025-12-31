# Issue #79: 로컬 LLM 속도 최적화

## 목표

현재 로컬 번역 모델(LFM2, Qwen, Yanolja)의 추론 속도를 최대화하여 사용자 경험을 개선합니다.

## 배경

- 현재 CPU Only 환경에서 LFM2 등 GGUF 모델 사용 시 속도가 느림
- `llama.cpp` 기반 엔진들의 연산량과 메모리 대역폭이 병목
- NLLB 엔진에서 CTranslate2 적용으로 유의미한 속도 개선 확인됨

## 조사된 최적화 방법

### 1. 🏃 n_threads 최적화 (즉시 적용 가능, 난이도: 하)

**원리**: 하이퍼스레딩 코어 전체 사용 시 컨텍스트 스위칭으로 오히려 느려짐. **물리 코어 수**만 할당하는 것이 최적.

**적용 방법**:
```python
import os
self.llm = Llama(
    model_path=self.model_path,
    n_ctx=4096,
    n_threads=os.cpu_count() // 2,  # 물리 코어 수만 할당
    verbose=False
)
```

**예상 효과**: 10~30% 속도 향상

---

### 2. 🛠️ AVX2/AVX-512 최적화 빌드 (설치 시 1회, 난이도: 중)

**원리**: 기본 `pip install`은 최적화 없이 빌드됨. AVX2 명령어 활성화 시 2~3배 빨라질 수 있음.

**적용 방법**:
```powershell
# Windows
pip uninstall llama-cpp-python -y
$env:CMAKE_ARGS = "-DGGML_AVX2=on"
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

```bash
# Linux/Mac
pip uninstall llama-cpp-python -y
CMAKE_ARGS="-DGGML_AVX2=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

**예상 효과**: 2~3배 속도 향상 (CPU에 따라 다름)

---

### 3. 🎮 CUDA GPU 가속 (GPU 필요, 난이도: 중)

**원리**: NVIDIA GPU가 있는 경우 CUDA로 10~50배 빠른 추론 가능.

**적용 방법**:
```powershell
# Windows (CUDA Toolkit 설치 필요)
pip uninstall llama-cpp-python -y
$env:CMAKE_ARGS = "-DGGML_CUDA=on"
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

**코드 변경**:
```python
self.llm = Llama(
    model_path=self.model_path,
    n_ctx=4096,
    n_gpu_layers=-1,  # 모든 레이어를 GPU로
    verbose=False
)
```

**예상 효과**: 10~50배 속도 향상

---

### 4. 📦 청크(Chunk) 단위 배치 번역 (구현 난이도: 상)

**원리**: 현재 "1문장 번역 → Reset → 1문장 번역" 방식은 오버헤드가 큼. 여러 문장을 한 번에 보내면 효율적.

**적용 방법**:
```python
def translate_batch_chunked(self, sentences, chunk_size=5):
    results = []
    for i in range(0, len(sentences), chunk_size):
        chunk = sentences[i:i+chunk_size]
        combined = "\n".join([f"<s{j}>{s}</s{j}>" for j, s in enumerate(chunk)])
        result = self.translate(combined, src, dest)
        # 결과 파싱하여 개별 문장으로 분리
        results.extend(parse_chunk_result(result))
    return results
```

**예상 효과**: 50~200% 속도 향상 (Reset 오버헤드 제거)

---

### 5. ⚡ CTranslate2 변환 (NLLB에서 검증됨, 난이도: 중)

**원리**: CTranslate2는 Transformer 모델 전용 최적화 추론 엔진. INT8 양자화 + 효율적 연산.

**현재 상태**: NLLB 엔진에서 이미 적용됨 (빠른 속도 확인)

**다른 모델 적용 가능성**:
- LFM2: 현재 CTranslate2 변환 버전 없음 (직접 변환 필요)
- Qwen: CTranslate2 미지원
- Yanolja: CTranslate2 미지원

---

### 6. 📊 더 작은 양자화 모델 사용 (Trade-off, 난이도: 하)

**원리**: Q4_K_M → Q3_K_M, IQ3_XS 등 더 작은 양자화 사용 시 속도 향상 (품질 저하 위험)

**적용 방법**: 모델 파일명만 변경
```python
# 현재
filename="LFM2-1.2B-Q4_K_M.gguf"
# 변경
filename="LFM2-1.2B-Q3_K_M.gguf"  # 더 작은 양자화
```

**예상 효과**: 20~40% 속도 향상 (품질 저하 가능)

---

### 7. 🚀 vLLM 적용 (고급, 난이도: 상)

**원리**: PagedAttention, Continuous Batching 등 고급 최적화 기법. 서버 환경에 적합.

**장점**:
- AWQ 양자화로 3배 빠른 처리량
- 대규모 배치 처리에 최적

**단점**:
- GPU 필수 (VRAM 8GB+)
- 복잡한 서버 설정 필요
- 현재 프로젝트 아키텍처와 맞지 않음

---

## 제안 변경 사항 (우선순위별)

### Phase 1: 즉시 적용 (코드 변경만)

#### [MODIFY] [lfm2.py](file:///c:/github/docling-translate/src/translation/engines/lfm2.py)

- `n_threads` 파라미터 추가 (물리 코어 수 기반)

#### [MODIFY] [lfm2_koen.py](file:///c:/github/docling-translate/src/translation/engines/lfm2_koen.py)

- `n_threads` 파라미터 추가

#### [MODIFY] [qwen.py](file:///c:/github/docling-translate/src/translation/engines/qwen.py)

- `n_threads` 파라미터 추가

#### [MODIFY] [yanolja.py](file:///c:/github/docling-translate/src/translation/engines/yanolja.py)

- `n_threads` 파라미터 추가

---

### Phase 2: 문서 안내 (README 업데이트)

#### [MODIFY] README.md, docs/README.en.md

**GPU 가속 설치 안내 추가**:
```bash
# CUDA GPU 가속 사용 시 (NVIDIA GPU 필요)
pip uninstall llama-cpp-python -y
$env:CMAKE_ARGS = "-DGGML_CUDA=on"  # Windows
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

**AVX2 최적화 빌드 안내 추가**:
```bash
# CPU 성능 최적화 빌드
pip uninstall llama-cpp-python -y
$env:CMAKE_ARGS = "-DGGML_AVX2=on"  # Windows
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

---

### Phase 3: 향후 고려 사항 (선택적)

- 청크 단위 배치 번역 구현 (구조 변경 필요)
- GPU 자동 감지 및 `n_gpu_layers` 자동 설정
- 더 작은 양자화 모델 옵션 제공

---

## 검증 계획

### 수동 테스트

**시나리오: n_threads 최적화 전/후 비교**
1. 현재 코드로 표준 샘플(`samples/1706.03762v7.pdf`) 번역 시간 측정
2. `n_threads` 적용 후 동일 파일로 번역 시간 측정
3. 속도 개선 비율 확인

---

## 예상 효과

| 최적화 방법 | 난이도 | 예상 속도 향상 | 비고 |
|------------|--------|---------------|------|
| n_threads 설정 | 하 | 10~30% | 즉시 적용 가능 |
| AVX2 빌드 | 중 | 2~3배 | 재설치 필요 |
| CUDA GPU | 중 | 10~50배 | GPU 필요 |
| 청크 배치 | 상 | 50~200% | 구조 변경 |
| 작은 양자화 | 하 | 20~40% | 품질 저하 가능 |

---

## 주의사항

- AVX2 빌드는 CPU가 AVX2 지원해야 함 (2013년 이후 Intel/AMD CPU 대부분 지원)
- CUDA 빌드는 CUDA Toolkit 설치 및 호환 드라이버 필요
- 청크 배치 번역은 프롬프트 설계와 파싱 로직 복잡도 증가

---

*계획 작성일: 2026-01-01*

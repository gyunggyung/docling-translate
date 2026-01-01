# Issue #92: Docling 속도 최적화 (CPU 병렬 처리)

## 목표

Docling 라이브러리의 CPU 병렬 처리 및 멀티스레딩 기능을 활성화하여, 현재 사용 가능한 CPU 리소스를 최대한 활용해 문서 변환 속도를 극대화합니다.

## 배경

`docling-translate`는 현재 싱글 스레드 또는 제한적인 멀티스레딩으로 동작할 가능성이 있습니다. Docling 공식 문서에 따르면 `OMP_NUM_THREADS` 환경 변수 설정과 내부 파이프라인 최적화를 통해 CPU 병렬 처리를 강화할 수 있다고 합니다. 이를 통해 대용량 문서 처리 시 속도 향상을 기대할 수 있습니다.

## 제안 변경 사항

### 1. 환경 변수 설정 (`src/core.py` 또는 진입점)

Docling 및 하위 라이브러리(PyTorch 등)가 로드되기 전에 CPU 스레드 수를 최대화하도록 환경 변수를 설정합니다.

#### [MODIFY] [src/core.py](file:///c:/github/docling-translate/src/core.py)

**변경 내용**:
- `os`, `multiprocessing` 모듈 임포트 추가
- `docling` 임포트 **이전**에 `OMP_NUM_THREADS` 환경 변수를 시스템의 CPU 코어 수로 설정
- (선택사항) `MKL_NUM_THREADS` 등 관련 변수도 함께 설정

**핵심 코드**:
```python
import os
import multiprocessing

# CPU 코어 수 확인 및 환경 변수 설정
# Docling 및 PyTorch가 임포트되기 전에 설정해야 효과적임
cpu_count = str(multiprocessing.cpu_count())
os.environ["OMP_NUM_THREADS"] = cpu_count
os.environ["MKL_NUM_THREADS"] = cpu_count  # Intel Math Kernel Library
os.environ["TORCH_NUM_THREADS"] = cpu_count # PyTorch

# ... 이후 docling 임포트 ...
from docling.document_converter import DocumentConverter
```

### 2. 가속기 사용 확인 (선택사항)

`DocumentConverter` 초기화 시 가속기(Accelerator) 옵션이 있는지 확인하고, CPU 모드에서 최적화된 설정을 적용합니다. (현재는 환경 변수가 가장 확실한 방법임)

---

## 검증 계획

### 1. 성능 비교 테스트 (수동)

**시나리오 1: 표준 샘플 변환 속도 측정**
- 단계:
  1. `samples/1706.03762v7.pdf` (또는 대용량 PDF)를 사용하여 변환 실행
  2. 변경 전/후의 "Conversion" 및 "Total Process" 시간 비교
- 예상 결과: CPU 사용률이 증가하고 변환 시간이 단축됨

### 2. 리소스 모니터링
- 작업 관리자 또는 `htop`을 통해 변환 도중 CPU 코어가 골고루 사용되는지(100% 부하 근접) 확인

---

## 예상 효과

- **성능**: 멀티코어 시스템에서 문서 변환(OCR, 레이아웃 분석) 단계의 속도가 현저히 개선될 것으로 예상됨 (최대 40% 이상 기대)
- **자원 효율성**: 유휴 CPU 코어를 적극적으로 활용

## 주의사항

- **메모리 사용량**: 스레드 수가 늘어나면 메모리 사용량도 증가할 수 있음. (OOM 주의)
- **오버헤드**: 너무 작은 문서의 경우 스레드 관리 오버헤드로 인해 오히려 느려질 수 있으나, 일반적으로 PDF 처리는 무거운 작업이므로 이점일 클 것임.

# 벤치마크 방법론 (Benchmark Methodology)

이 문서는 `docling-translate` 프로젝트의 성능 측정 방식과 지표를 정의합니다.

## 측정 철학
우리는 "공정한 시간 측정(Fair Time Checking)"을 지향합니다. 사용자가 체감하는 전체 실행 시간뿐만 아니라, 각 단계별(I/O, 연산, 네트워크) 소요 시간을 정밀하게 분리하여 병목 구간을 식별하는 것을 목표로 합니다.

## 측정 지표 (Metrics)

### 1. 시간 지표 (Time Metrics)
모든 시간은 `Wall Time` (실제 경과 시간)을 기준으로 측정합니다.

- **Import Libraries**: 프로그램 시작 후 `docling` 등 무거운 라이브러리를 로딩하는 데 걸리는 시간입니다.
- **Initialization**: `DocumentConverter` 모델을 메모리에 올리고 초기화하는 시간입니다.
- **Total Batch Execution**: 실제 PDF 처리(변환+번역)가 시작되어 끝날 때까지의 총 시간입니다. (병렬 처리 시 이 시간이 중요합니다.)
- **Total Process (Per File)**: 개별 파일 처리에 걸린 총 시간입니다.
- **Conversion**: PDF를 `DoclingDocument` 구조로 변환하는 시간입니다. (CPU/GPU 연산 위주)
- **Translation & Save**: 텍스트를 추출하여 번역하고 결과를 파일로 저장하는 시간입니다. (네트워크 I/O 위주)

### 2. 통계 지표 (Statistical Metrics)
단순 시간 외에 작업량 대비 속도를 측정합니다.

- **Image Save**:
    - `Count`: 저장된 이미지 개수.
    - `Avg Time`: 이미지 1장당 평균 저장 시간.
- **Translation (Sentences)**:
    - `Count`: 번역된 문장 수.
    - `Avg Time`: 문장당 평균 번역 API 호출 시간.
    - `Throughput`: 초당 처리된 글자 수 (Chars/sec).

### 3. 실행 메타데이터
벤치마크 리포트에는 다음 정보도 표시됩니다:

- **실행 모드**: Sequential (순차) / Parallel (병렬)
- **워커 수 (max-workers)**: 병렬 처리 스레드 수

## 벤치마크 실행 방법

### 기본 실행 (벤치마크 끄기)
```bash
python main.py samples/
```
일반적인 사용 시에는 벤치마크 오버헤드가 없습니다.

### 벤치마크 모드
```bash
python main.py samples/ --benchmark
```
상세 리포트가 콘솔에 출력되고 `docs/BENCHMARK_LOG.md`에 저장됩니다.

### 순차 실행 (비교용)
```bash
python main.py samples/ --benchmark --sequential
```
병렬 처리를 끄고 순차적으로 실행하여 성능 차이를 비교할 수 있습니다.

### 워커 수 조절
```bash
python main.py samples/ --max-workers 8 --benchmark
```
병렬 처리 워커 수를 직접 지정할 수 있습니다. (기본값: 4)

## 리포트 해석 가이드

```text
============================================================
벤치마크 리포트 (2025-11-22 08:04:17)
============================================================
실행 모드: 병렬(Parallel)      ← 순차/병렬 여부
워커 수 (max-workers): 8       ← 병렬 처리 스레드 수
------------------------------------------------------------
전체 실행 시간: 110.03초
------------------------------------------------------------
작업명                                      | 소요 시간     
------------------------------------------------------------
Import Libraries                         | 7.58초      ← 라이브러리 로딩 (최적화 어려움)
Initialization                           | 0.00초      ← 모델 초기화 (1회만 발생)
Total Batch Execution                    | 110.02초    ← 실제 작업 시간
Conversion: 1706.03762v7.pdf             | 59.22초     ← PDF 변환 (CPU/GPU 작업)
Translation & Save: 1706.03762v7.pdf     | 50.79초     ← 번역 및 저장 (네트워크 I/O)
------------------------------------------------------------
통계 항목                          | 횟수     | 평균 시간      | 처리량 (Throughput)
------------------------------------------------------------
Translation (Sentences)        | 405    | 0.1249초    | 731.7 chars/초
Image Save                     | 10     | 0.0184초    | 
------------------------------------------------------------
```

**해석 팁**:
- **Throughput**이 낮다면 네트워크 상태나 API 응답 속도를 점검해야 합니다.
- **Image Save** 시간이 길다면 디스크 I/O가 병목일 수 있습니다.
- **Translation & Save**가 전체의 큰 비중을 차지하면 병렬 처리로 개선 가능합니다.

## 결론

벤치마크 리포트를 통해:
- 전체 처리 시간 파악 가능
- 병목 구간 식별 (Conversion vs Translation)
- 병렬 처리 효과 측정 가능
- 최적 워커 수 결정에 활용

벤치마크 기능을 사용하여 지속적인 성능 개선을 추구합니다.

---

## Bulk Translation 전략

### 개요
Bulk Translation은 문장 단위 병렬 번역을 통해 번역 성능을 극대화하는 전략입니다.

### 동작 원리

**전통적인 방식**:
```python
for each TextItem:
    for each sentence in TextItem:
        translate(sentence)  # 순차 처리, 네트워크 대기 병목
```

**Bulk Translation 방식**:
```python
# Phase 1: Collection (문장 수집)
all_sentences = []
for each TextItem:
    all_sentences.extend(sentences)

# Phase 2: Bulk Translation (일괄 병렬 번역)
with ThreadPoolExecutor(max_workers=8):
    translated = parallel_translate(all_sentences)

# Phase 3: Generation (파일 생성)
for each TextItem:
    get translation from map
    write to file
```

### 핵심 이점

1. **네트워크 대기 시간 최소화**
   - 번역 API 호출은 네트워크 I/O 대기가 주 병목
   - 여러 문장을 동시에 요청하면 대기 시간이 병렬로 진행
   - 8 workers로 약 4.7배 속도 향상 (239초 → 51초)

2. **코드 구조 명확성**
   - Collection, Translation, Generation 단계 분리
   - 각 단계의 책임이 명확함
   - 디버깅 및 유지보수 용이

3. **확장성**
   - Worker 수 조절로 성능 튜닝 가능
   - 다양한 번역 엔진에 적용 가능

### 성능 결과

순차 처리 vs 병렬 처리 (8 workers) 비교:
- **전체 시간**: 341초 → 110초 (**68% 단축, 3.1배 빨라짐**)
- **번역 시간**: 239초 → 51초 (**79% 단축, 4.7배 빨라짐**)
- **처리량**: 155 → 732 chars/초 (**4.7배 향상**)

상세 비교는 `docs/PERFORMANCE_COMPARISON.md` 참조.

---

*최종 업데이트: 2025-11-22*

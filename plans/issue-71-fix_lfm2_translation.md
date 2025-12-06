# Issue #71: LFM2 번역 오류 수정

## 목표

LiquidAI LFM2-1.2B-GGUF 모델을 사용하는 번역 엔진(`lfm2.py`)의 오류를 수정하고, 올바른 사용법을 검증하여 안정적인 번역 기능을 제공합니다.

## 배경

Issue #71에 따르면 현재 LFM2 번역 엔진이 정상적으로 동작하지 않거나 품질이 좋지 않은 문제가 있습니다. `llama-cpp-python` 라이브러리를 직접 사용하여 모델의 동작을 검증하고, 이를 토대로 엔진 코드를 수정해야 합니다. 공식 문서에 따르면 LFM2는 ChatML 프롬프트 형식을 사용해야 합니다.

## 제안 변경 사항

### 번역 엔진

#### [MODIFY] [lfm2.py](file:///c:/github/docling-translate/src/translation/engines/lfm2.py)

**변경 내용**:
- `llama_cpp` 사용법 재검증 및 적용
- 모델 로드 및 프롬프트 구성 방식 개선 (ChatML 형식 적용)
- 에러 처리 및 디버깅 로그 강화

**핵심 코드 (수정됨)**:
```python
# ChatML 프롬프트 형식 적용
prompt = f"""<|im_start|>user
Translate the following text from {src_name} to {dest_name}.

Text:
{text}<|im_end|>
<|im_start|>assistant
"""
# stop 토큰 업데이트: ["<|im_end|>"]
```

### 디버깅 도구

#### [NEW] [debug_lfm2_manual.py](file:///c:/github/docling-translate/debug_lfm2_manual.py)

**목적**: LFM2 모델의 `llama-cpp-python` 동작을 독립적으로 검증하기 위함

**주요 기능**:
- `huggingface_hub`를 통한 모델 다운로드 (LFM2-1.2B-Q4_K_M.gguf)
- `llama_cpp.Llama` 인스턴스 초기화 및 ChatML 형식 프롬프트 테스트
- 한국어 주석 포함

---

## 검증 계획

### 1. 수동 테스트

**시나리오 1: 직접 사용 스크립트 실행**
- 단계:
  1. `python debug_lfm2_manual.py` 실행
  2. 모델 다운로드 및 로드 성공 확인
  3. 테스트 문장("The quick brown fox...") 번역 결과 확인 (한국어 출력)
- 예상 결과: 정상적인 한국어 번역 결과 출력

**시나리오 2: 전체 파이프라인 테스트**
- 단계:
  1. `python main.py samples/1706.03762v7.pdf --engine lfm2` 실행
  2. PDF 번역 완료 및 결과 확인
- 예상 결과: 에러 없이 번역된 문서 생성

### 2. 검증 체크리스트

- [ ] `debug_lfm2_manual.py` 실행 성공 (ChatML 형식 검증)
- [ ] `lfm2.py` 수정 후 `main.py` 연동 테스트 성공
- [ ] 표준 샘플(`samples/1706.03762v7.pdf`) 변환 테스트

---

## 예상 효과

- **안정성**: LFM2 엔진의 번역 실패 문제 해결
- **품질**: 올바른 프롬프트(ChatML) 사용으로 번역 품질 및 지시 이행 능력 향상

---

## 주의사항

- `llama-cpp-python` 설치 필요
- 모델 파일 크기(약 1.2GB)
- ChatML 특수 토큰 처리가 `llama-cpp-python`에서 잘 동작하는지 확인 필요

---

*계획 작성일: 2025-12-07*

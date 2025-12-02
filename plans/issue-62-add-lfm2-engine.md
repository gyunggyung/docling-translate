# Issue #62: 번역 엔진 추가 LFM2

## 목표

LiquidAI의 LFM2-1.2B 모델을 새로운 번역 엔진으로 추가하여, 빠르고 성능 좋은 한국어-영어 번역 기능을 제공합니다.

## 배경

LFM2-1.2B는 LiquidAI에서 공개한 효율적인 하이브리드 모델로, 한국어와 영어 간의 번역 성능이 우수하고 속도가 빠른 것으로 알려져 있습니다. 기존 HuggingFace 기반 엔진(Qwen 등)과 유사한 방식으로 GGUF 모델을 활용하여 로컬 환경에서 실행 가능한 번역 엔진을 구현하고자 합니다.

## 제안 변경 사항

### 번역 엔진 (Translation Engines)

#### [NEW] [src/translation/engines/lfm2.py](file:///c:/github/docling-translate/src/translation/engines/lfm2.py)

**목적**: LFM2-1.2B-GGUF 모델을 로드하고 번역을 수행하는 엔진 클래스 구현

**주요 기능**:
- `huggingface_hub`를 통해 `LiquidAI/LFM2-1.2B-GGUF` 모델 다운로드
- `llama_cpp`를 사용하여 모델 로드
- LFM2의 프롬프트 형식에 맞춰 번역 요청 생성 (Chat Completion API 또는 수동 프롬프트 구성 활용)
- 번역 결과 후처리 (태그 제거 등)

**핵심 코드 (예시)**:
```python
class LFM2Translator(BaseTranslator):
    def __init__(self):
        # 모델 다운로드 및 로드
        self.model_path = hf_hub_download(
            repo_id="LiquidAI/LFM2-1.2B-GGUF",
            filename="LFM2-1.2B-Q4_K_M.gguf" # 파일명 확인 필요
        )
        self.llm = Llama(model_path=self.model_path, n_ctx=4096)

    def translate(self, text, src, dest):
        # 프롬프트 구성 및 생성
        messages = [
            {"role": "system", "content": "You are a professional translator..."},
            {"role": "user", "content": text}
        ]
        output = self.llm.create_chat_completion(messages=messages)
        return output['choices'][0]['message']['content']
```

#### [MODIFY] [src/translation/__init__.py](file:///c:/github/docling-translate/src/translation/__init__.py)

**변경 내용**:
- `LFM2Translator` 클래스 임포트
- `create_translator` 함수 내 `engines` 딕셔너리에 `lfm2` 키 추가

#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)

**변경 내용**:
- 사이드바의 엔진 선택 옵션(`selectbox`)에 `lfm2` 추가
- `lfm2` 선택 시 기본 워커 수 설정 (로컬 모델이므로 1로 설정)

#### [MODIFY] [README.md](file:///c:/github/docling-translate/README.md)

**변경 내용**:
- 지원되는 번역 엔진 목록에 LFM2 추가
- 모델 정보 및 특징(속도, 성능) 간략 기술

## 검증 계획

### 1. 모델 파일명 및 프롬프트 확인
- `LiquidAI/LFM2-1.2B-GGUF` 리포지토리의 실제 파일명 확인 (`LFM2-1.2B-Q4_K_M.gguf` 등)
- 모델이 사용하는 정확한 Chat Template 확인 (Jinja 템플릿 또는 특수 토큰)

### 2. 수동 테스트
- **시나리오**: 표준 샘플 PDF(`samples/1706.03762v7.pdf`)를 LFM2 엔진으로 번역
- **단계**:
  1. `streamlit run app.py` 실행
  2. 언어 설정: 영어 -> 한국어
  3. 엔진 선택: `lfm2`
  4. 파일 업로드 및 번역 실행
- **예상 결과**:
  - 모델 다운로드가 정상적으로 진행됨
  - 번역이 에러 없이 완료됨
  - 번역된 결과물의 품질이 양호하고, 문장이 자연스러움

### 3. 검증 체크리스트
- [ ] LFM2 모델 다운로드 및 로드 성공
- [ ] 프롬프트 형식이 모델에 적합하게 적용됨
- [ ] 한국어 번역 결과가 정상적으로 출력됨
- [ ] 기존 엔진(Google, DeepL 등) 동작에 영향 없음

## 예상 효과

- **성능**: 가볍고 빠른 LFM2 모델을 통해 로컬 환경에서도 준수한 속도의 번역 제공
- **품질**: 최신 LLM 기술이 적용된 모델로, 특히 기술 문서 번역에서 좋은 성능 기대
- **비용**: 외부 API 비용 없이 고품질 번역 가능

## 주의사항

- **메모리 사용량**: 1.2B 모델이지만 로컬 실행 시 메모리 점유율 확인 필요
- **프롬프트 호환성**: LFM2의 고유한 프롬프트 형식을 지키지 않을 경우 성능 저하 가능성 있음
- **GGUF 호환성**: `llama_cpp` 버전과 모델의 호환성 확인 필요

*계획 작성일: 2025-12-02*

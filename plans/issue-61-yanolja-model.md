# Issue #61: 번역 엔진 추가 (YanoljaNEXT-Rosetta-4B-2511-GGUF)

## 목표

한국어 번역 성능이 우수한 `yanolja/YanoljaNEXT-Rosetta-4B-2511-GGUF` 모델을 새로운 번역 엔진으로 추가합니다.

## 배경

기존 Qwen 모델 추가(Issue #60)와 유사하게, 로컬에서 실행 가능한 고성능 한국어 번역 모델을 지원하여 사용자의 선택지를 넓히고 번역 품질을 향상시키고자 합니다. 해당 모델은 야놀자에서 공개한 것으로, 특히 구조화된 데이터 번역에 강점이 있으나 일반 텍스트 번역에도 우수한 성능을 보일 것으로 기대됩니다.

## 제안 변경 사항

### 번역 엔진 (Translation Engine)

#### [NEW] [src/translation/engines/yanolja.py](file:///c:/github/docling-translate/src/translation/engines/yanolja.py)

**목적**: YanoljaNEXT-Rosetta-4B-2511-GGUF 모델을 사용하는 번역기 구현

**주요 기능**:
- `huggingface_hub`를 통해 `yanolja/YanoljaNEXT-Rosetta-4B-2511-GGUF` 모델 다운로드 (Q5_K_M 양자화 버전 사용 권장)
- `llama_cpp`를 사용하여 모델 로드 (Context Size 4096 설정)
- 모델 전용 Prompt Template 적용 (`<start_of_turn>instruction ... <end_of_turn>`)
- `BaseTranslator` 상속 및 `translate` 메서드 구현

**핵심 코드**:
```python
class YanoljaTranslator(BaseTranslator):
    def __init__(self):
        # ... 모델 다운로드 및 로드 ...
        self.model_path = hf_hub_download(
            repo_id="yanolja/YanoljaNEXT-Rosetta-4B-2511-GGUF",
            filename="YanoljaNEXT-Rosetta-4B-2511-q5_k_m.gguf"
        )
        self.llm = Llama(model_path=self.model_path, n_ctx=4096, ...)

    def translate(self, text, src, dest):
        # ... 프롬프트 구성 ...
        prompt = f"""<start_of_turn>instruction
Translate the following text from {src_name} to {dest_name}.
Provide the final translation immediately without any other text.
<end_of_turn>
<start_of_turn>source
{text}
<end_of_turn>
<start_of_turn>translation
"""
        # ... 생성 및 후처리 ...
```

---

#### [MODIFY] [src/translation/__init__.py](file:///c:/github/docling-translate/src/translation/__init__.py)

**변경 내용**:
- `YanoljaTranslator` 임포트
- `create_translator` 함수의 `engines` 딕셔너리에 "yanolja" 키 추가

**핵심 코드**:
```python
from .engines.yanolja import YanoljaTranslator

def create_translator(engine_name: str) -> BaseTranslator:
    engines = {
        # ... 기존 엔진들 ...
        "yanolja": YanoljaTranslator,
    }
    # ...
```

---

## 검증 계획

### 1. 수동 테스트

**시나리오 1: Yanolja 모델로 샘플 PDF 번역**
- 단계:
  1. `main.py`를 실행하여 `yanolja` 엔진으로 번역 수행
     ```bash
     python main.py --engine yanolja samples/1706.03762v7.pdf
     ```
  2. 모델 다운로드 진행률 확인
  3. 번역 로그 확인 (에러 없이 진행되는지)
  4. 생성된 결과물(`output/1706.03762v7_translated.md` 등) 확인

- 예상 결과:
  - 모델이 정상적으로 다운로드되고 로드됨
  - 번역이 수행되어 결과 파일이 생성됨
  - 번역 품질이 양호하고 한국어로 정상 번역됨

### 2. 검증 체크리스트

- [ ] `src/translation/engines/yanolja.py` 파일 생성 및 구현
- [ ] `src/translation/__init__.py`에 엔진 등록
- [ ] `python main.py --engine yanolja ...` 실행 시 정상 동작 확인
- [ ] 번역 결과물의 품질 및 형식 확인

---

## 예상 효과

- **품질**: 한국어에 특화된 최신 모델을 사용하여 번역 품질 향상 기대
- **선택권**: 사용자가 로컬 환경에서 사용할 수 있는 고성능 모델 옵션 추가

---

## 주의사항

- **메모리 사용량**: 4B 모델이므로 약 3~4GB 이상의 VRAM 또는 RAM이 필요할 수 있음 (Q5_K_M 기준)
- **속도**: CPU 실행 시 속도가 느릴 수 있음
- **프롬프트**: 모델이 지시사항을 잘 따르는지 확인 필요 (불필요한 설명 출력 방지)

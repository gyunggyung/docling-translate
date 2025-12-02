# Issue #60: 번역 엔진 추가 Qwen3-0.6B-GGUF

## 목표
- `Qwen3-0.6B-GGUF` 모델을 사용하는 로컬 번역 엔진을 추가합니다.
- **기술 선택 이유**: Windows CPU 환경에서 GGUF 모델을 구동하기 위해 가장 널리 사용되고 최적화(AVX/NEON 등)가 잘 된 `llama-cpp-python`을 사용합니다. `ctransformers` 대비 유지보수가 활발하고 기능이 풍부합니다.
- **모델 태그**: CLI에서는 `qwen-0.6b`를 사용하며, 내부적으로는 `qwen_0_6b`로 관리합니다. 추후 `qwen-4b` 등 확장을 고려한 네이밍입니다.

## 사용자 리뷰 필요 사항
- **라이브러리 추가**: `llama-cpp-python`과 `huggingface_hub`가 `requirements.txt`에 추가됩니다.
- **모델 다운로드**: 최초 실행 시 약 0.6GB의 모델 파일을 다운로드합니다. (기본 경로: HuggingFace Cache)

## 변경 제안

### 1. 의존성 추가
#### [MODIFY] [requirements.txt](file:///c:/github/docling-translate/requirements.txt)
- `llama-cpp-python>=0.2.0`
- `huggingface_hub>=0.19.0`

### 2. 번역 엔진 구현
#### [NEW] [src/translation/engines/qwen.py](file:///c:/github/docling-translate/src/translation/engines/qwen.py)
- `BaseTranslator`를 상속받는 `QwenTranslator` 클래스 구현.
- **사용 모델**: `Qwen/Qwen3-0.6B-GGUF` (파일명: `qwen3-0.6b-instruct-q4_k_m.gguf` 등 권장 양자화 사용)
- **프롬프트 템플릿 (ChatML)**:
    ```python
    <|im_start|>system
    You are a professional translator. Translate the following text from {src} to {dest}.<|im_end|>
    <|im_start|>user
    {text}<|im_end|>
    <|im_start|>assistant
    ```
- **구현 상세**:
    ```python
    from llama_cpp import Llama
    from huggingface_hub import hf_hub_download

    class QwenTranslator(BaseTranslator):
        def __init__(self):
            model_path = hf_hub_download(
                repo_id="Qwen/Qwen3-0.6B-GGUF",
                filename="qwen3-0.6b-instruct-q8_0.gguf" # 또는 q4_k_m
            )
            self.llm = Llama(
                model_path=model_path,
                n_ctx=2048,
                verbose=False
            )

        def translate(self, text, src, dest):
            prompt = f"""<|im_start|>system
You are a professional translator. Translate the following text from {src} to {dest}.<|im_end|>
<|im_start|>user
{text}<|im_end|>
<|im_start|>assistant
"""
            output = self.llm(
                prompt,
                max_tokens=1024,
                stop=["<|im_end|>"],
                echo=False
            )
            return output['choices'][0]['text'].strip()
    ```

### 3. 엔진 통합
#### [MODIFY] [src/translation/utils.py](file:///c:/github/docling-translate/src/translation/utils.py)
- `get_translator` 함수 수정:
    - `engine='qwen-0.6b'` (또는 `qwen`) 입력 시 `QwenTranslator` 반환.

#### [MODIFY] [main.py](file:///c:/github/docling-translate/main.py)
- CLI 인자 `--engine` 옵션에 `qwen-0.6b` 추가.

#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)
- 사이드바 번역 엔진 선택 옵션에 `qwen-0.6b` 추가.

## 검증 계획

### 자동화 테스트
- `tests/test_qwen.py` (임시) 생성하여 간단한 문장("Hello world") 번역 테스트 실행.
    ```bash
    python tests/test_qwen.py
    ```

### 수동 검증
- 표준 샘플 파일(`samples/1706.03762v7.pdf`)을 사용하여 번역 실행.
    ```bash
    python main.py --input samples/1706.03762v7.pdf --engine qwen-0.6b
    ```
- 생성된 결과물 확인 및 번역 품질/속도 체감.

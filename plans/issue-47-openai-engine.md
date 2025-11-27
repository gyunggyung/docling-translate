# Issue #47: 번역 엔진 추가 OpenAI

## 목표

OpenAI의 GPT 모델을 번역 엔진으로 추가하여, 사용자가 Google, DeepL, Gemini와 함께 OpenAI GPT를 번역 옵션으로 사용할 수 있도록 합니다.

## 배경

현재 `docling-translate`는 Google Translate, DeepL, Gemini를 지원하지만, OpenAI의 GPT 모델은 지원하지 않습니다. [Issue #47](https://github.com/gyunggyung/docling-translate/issues/47)에서 요청된 대로, 다음 세 가지를 구현해야 합니다:

1. GPT 번역 엔진 추가
2. 적절한 모델 선택: **GPT-5-nano** 사용
3. 다국어 번역에 최적화된 프롬프트 작성

**모델 선택**:
- **GPT-5-nano**: 최신 모델, 빠르고 효율적, 기술 문서 번역에 최적화
- OpenAI의 새로운 Responses API (`client.responses.create()`) 사용

**API 키 관리**:
- 기존 프로젝트에서 사용 중인 `.env` 파일 방식 활용
- `python-dotenv`가 이미 설치되어 있어 추가 의존성 불필요

## 제안 변경 사항

### 번역 엔진 모듈

#### [MODIFY] [translator.py](file:///c:/github/docling-translate/translator.py)

**변경 내용**:
- OpenAI SDK import 추가 (선택적 import로 처리)
- `OPENAI_API_KEY` 환경 변수 읽기 추가
- `_openai_client` 전역 변수로 클라이언트 싱글톤 패턴 적용 (효율성 개선)
- `_translate_with_openai()` 함수 추가
- `translate_text()` 함수에 `"openai"` 엔진 분기 추가

**최적화 방안**:
현재 `translator.py`의 구조를 다음과 같이 개선합니다:
1. **클라이언트 싱글톤**: OpenAI 클라이언트를 전역 변수로 초기화하여 매번 재생성 방지 (DeepL 패턴과 동일)
2. **코드 일관성**: Gemini도 전역 클라이언트로 변경하여 모든 API가 동일한 패턴 사용
3. **효율성**: 함수 호출마다 클라이언트 생성 오버헤드 제거

```python
# Import 섹션에 추가
try:
    from openai import OpenAI  # openai 공식 SDK
except ImportError:
    OpenAI = None

# 환경 변수 섹션 (DeepL, Gemini 키 읽기 부분 바로 뒤에 추가)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# 전역 클라이언트 초기화 (DeepL 패턴과 동일하게 싱글톤으로 관리)
_openai_client = None
if OpenAI is not None and OPENAI_API_KEY:
    try:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
        _log.info("OpenAI 클라이언트 초기화 성공")
    except Exception as e:
        _log.warning("OpenAI 클라이언트 초기화 실패: %s", e)
        _openai_client = None

# 번역 함수 추가 (엔진별 로우레벨 번역 함수 섹션에 추가)
def _translate_with_openai(
    text: str, 
    src: str, 
    dest: str,
    model: str = "gpt-5-nano"  # GPT-5-nano 사용
) -> str:
    """
    OpenAI GPT-5-nano 모델로 번역
    - Responses API 사용 (client.responses.create)
    - 429 / 503 에러 시 재시도 (최대 3번)
    - 실패 시 Google 번역으로 fallback
    """
    # 클라이언트가 초기화되지 않은 경우 → Google로 fallback
    if _openai_client is None:
        if OpenAI is None:
            _log.error("openai 패키지가 설치되어 있지 않습니다. Google 번역으로 fallback.")
        else:
            _log.error("OPENAI_API_KEY가 설정되지 않았거나 클라이언트 초기화 실패. Google 번역으로 fallback.")
        return _translate_with_google(text, src, dest)

    # 최대 3번까지 재시도
    for attempt in range(3):
        try:
            # 기술 문서 번역에 최적화된 프롬프트
            translation_input = (
                f"Translate the following text from {src} to {dest}. "
                f"You are a professional translator specialized in technical documentation. "
                f"Maintain the original formatting, technical terms, and tone. "
                f"Provide ONLY the translated text without any explanations.\n\n"
                f"{text}"
            )

            # OpenAI Responses API 호출 (GPT-5-nano)
            response = _openai_client.responses.create(
                model=model,
                input=translation_input
            )

            # 정상 응답: output_text 속성 사용
            if hasattr(response, 'output_text') and response.output_text:
                return response.output_text.strip()

            raise RuntimeError("OpenAI 응답에 output_text가 없습니다.")

        except Exception as e:
            msg = str(e)

            # 429 / 503 같이 재시도 가능한 에러
            retriable = (
                "429" in msg or "503" in msg 
                or "rate_limit" in msg.lower() 
                or "overloaded" in msg.lower()
            )

            if retriable and attempt < 2:
                wait = 2 ** attempt  # 1초 → 2초 → 4초
                _log.warning(
                    "OpenAI 호출 실패(시도 %d/3, %ss 후 재시도): %s",
                    attempt + 1, wait, msg
                )
                time.sleep(wait)
                continue

            # 재시도 불가하거나 마지막 시도
            _log.error("OpenAI 번역 최종 실패, Google로 fallback: %s", msg)
            break

    # 모든 재시도 실패 → Google 번역으로 fallback
    return _translate_with_google(text, src, dest)

# translate_text() 함수의 엔진 분기에 추가
elif engine == "openai":
    translated = _translate_with_openai(text, src, dest)
```

**주요 개선 사항**:
1. ✅ **전역 클라이언트**: `_openai_client`를 모듈 로드 시 한 번만 초기화 (DeepL과 동일한 패턴)
2. ✅ **효율성**: 매번 `OpenAI()` 객체를 생성하지 않아 오버헤드 제거
3. ✅ **간결성**: 클라이언트 초기화 로직을 함수 밖으로 분리하여 코드 간소화
4. ✅ **일관성**: DeepL의 `_deepl_client` 패턴과 동일하게 구현

**추가 리팩토링 (선택 사항)**:
- Gemini도 동일한 패턴으로 변경: `_gemini_client` 전역 변수로 관리
- 이렇게 하면 모든 API 클라이언트가 일관된 패턴을 따름
- 코드 가독성과 유지보수성 향상

---

### CLI 및 Web UI

#### [MODIFY] [main.py](file:///c:/github/docling-translate/main.py)

**변경 내용**:
- `--engine` 인자의 choices에 `"openai"` 추가
- 도움말 텍스트 업데이트

**핵심 코드**:
```python
parser.add_argument(
    "--engine",
    type=str,
    default="google",
    choices=["google", "deepl", "gemini", "openai"],  # openai 추가
    help="번역 엔진 선택 (기본값: google)",
)
```

---

#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)

**변경 내용**:
- Streamlit selectbox의 options에 `"OpenAI (GPT-5-nano)"` 추가
- 엔진 매핑 딕셔너리에 `"OpenAI (GPT-5-nano)": "openai"` 추가
- 설정 안내 메시지에 `.env` 파일에 `OPENAI_API_KEY` 추가 안내

**핵심 코드**:
```python
# 엔진 선택 (한국어 + 영어 모두 지원)
if current_lang == "ko":
    engine_display = st.selectbox(
        "번역 엔진",
        ["Google Translate (무료)", "DeepL (API 키 필요)", "Gemini (API 키 필요)", "OpenAI GPT-5-nano (API 키 필요)"],
        help="사용할 번역 엔진을 선택하세요."
    )
    engine_map = {
        "Google Translate (무료)": "google",
        "DeepL (API 키 필요)": "deepl",
        "Gemini (API 키 필요)": "gemini",
        "OpenAI GPT-5-nano (API 키 필요)": "openai",
    }
else:
    engine_display = st.selectbox(
        "Translation Engine",
        ["Google Translate (Free)", "DeepL (API Key Required)", "Gemini (API Key Required)", "OpenAI GPT-5-nano (API Key Required)"],
        help="Select the translation engine to use."
    )
    engine_map = {
        "Google Translate (Free)": "google",
        "DeepL (API Key Required)": "deepl",
        "Gemini (API Key Required)": "gemini",
        "OpenAI GPT-5-nano (API Key Required)": "openai",
    }
```

---

### 의존성 및 문서

#### [MODIFY] [requirements.txt](file:///c:/github/docling-translate/requirements.txt)

**변경 내용**:
- `openai` 패키지 추가 (v2.8.1 이상)

```txt
openai>=2.8.0
```

---

#### [NEW] [.env.example](file:///c:/github/docling-translate/.env.example)

**목적**: 사용자가 `.env` 파일을 쉽게 설정할 수 있도록 예시 파일 제공

**내용**:
```bash
# OpenAI API 키 (https://platform.openai.com/api-keys에서 발급)
OPENAI_API_KEY=sk-proj-your-api-key-here

# DeepL API 키 (선택 사항)
DEEPL_API_KEY=your-deepl-key-here

# Gemini API 키 (선택 사항)
GEMINI_API_KEY=your-gemini-key-here
```

**사용 방법**:
- `.env.example`을 `.env`로 복사하여 실제 API 키 입력
- `.env` 파일은 `.gitignore`에 이미 등록되어 있음

---

#### [MODIFY] [README.md](file:///c:/github/docling-translate/README.md)

**변경 내용**:
- 지원 엔진 목록에 OpenAI 추가
- OpenAI API 키 설정 방법 추가
- 모델 선택 가이드 추가

**추가 내용**:
```markdown
### 지원 번역 엔진

- **Google Translate** (기본값, 무료)
- **DeepL** (API 키 필요, 고품질)
- **Gemini** (API 키 필요, Google AI)
- **OpenAI GPT-5-nano** (API 키 필요, 최신 모델) ← 새로 추가

### OpenAI 설정

1. [OpenAI Platform](https://platform.openai.com/api-keys)에서 API 키 생성
2. 프로젝트 루트에 `.env` 파일 생성 후 API 키 추가:
   ```bash
   OPENAI_API_KEY=sk-proj-...
   ```

**모델 정보**:
- 사용 모델: `gpt-5-nano` (최신 모델, 빠르고 효율적)
- Responses API 사용 (OpenAI의 새로운 API)
```

---

#### [MODIFY] [docs/README.en.md](file:///c:/github/docling-translate/docs/README.en.md)

**변경 내용**:
- 영어 문서에도 동일하게 OpenAI 관련 정보 추가

---

## 검증 계획

### 1. 수동 테스트

**시나리오 1: CLI에서 OpenAI 엔진 사용**
- 단계:
  1. `OPENAI_API_KEY` 환경 변수 설정
  2. `python main.py samples/1706.03762v7.pdf ko --engine openai` 실행
  3. 생성된 HTML 파일에서 번역 품질 확인
- 예상 결과: 
  - 번역이 정상적으로 수행됨
  - 기술 용어가 자연스럽게 번역됨
  - 원문과 번역문이 정확히 매칭됨

**시나리오 2: Web UI에서 OpenAI 선택**
- 단계:
  1. `streamlit run app.py` 실행
  2. "OpenAI (API 키 필요)" 선택
  3. PDF 업로드 및 번역
- 예상 결과:
  - OpenAI 엔진이 정상 작동
  - 진행률 표시가 정확함

**시나리오 3: API 키가 없는 경우 Fallback**
- 단계:
  1. `OPENAI_API_KEY` 미설정 상태에서 `--engine openai` 실행
  2. 로그 메시지 확인
- 예상 결과:
  - "OPENAI_API_KEY가 설정되어 있지 않습니다" 경고 출력
  - Google 번역으로 자동 fallback

**시나리오 4: Rate Limit 발생 시 재시도**
- 단계:
  1. Rate limit에 걸릴 만큼 빠르게 여러 요청 전송
  2. 로그 확인
- 예상 결과:
  - "OpenAI 호출 실패(시도 X/3)" 로그 출력
  - 자동 재시도 후 성공 또는 fallback

### 2. 검증 체크리스트

- [ ] `openai` 패키지가 선택적으로 import되어, 미설치 시에도 다른 엔진은 정상 작동
- [ ] CLI에서 `--engine openai` 옵션이 정상 작동
- [ ] Web UI에서 "OpenAI" 선택이 정상 작동
- [ ] API 키가 없을 때 적절한 에러 메시지 출력 및 fallback
- [ ] Rate limit 발생 시 자동 재시도 로직 작동
- [ ] 표준 샘플(`samples/1706.03762v7.pdf`)로 테스트
- [ ] 기존 엔진(google, deepl, gemini)이 정상 동작하는지 확인
- [ ] 번역 품질이 Gemini와 비슷하거나 더 나은지 확인

---

## 예상 효과

- **선택의 폭 확대**: 사용자가 4가지 번역 엔진 중 선택 가능
- **품질 향상**: OpenAI GPT는 기술 문서 번역에서 높은 품질 제공
- **비용 효율성**: gpt-5-nano는 매우 저렴 (입력 $0.05/1M, 출력 $0.40/1M 토큰)
- **안정성**: 재시도 로직과 fallback으로 높은 가용성 보장

---

## 주의사항

1. **OpenAI API 비용**:
   - **gpt-5-nano**: 입력 $0.05/1M 토큰, 출력 $0.40/1M 토큰 (매우 저렴)
   - 참고: gpt-5-mini ($0.25/$2.00), gpt-5 ($1.25/$10.00)
   - 대량 번역에도 비용 부담이 낮음

2. **Rate Limiting**:
   - OpenAI API는 tier별 rate limit 존재
   - 재시도 로직으로 어느 정도 대응하지만, 대량 처리 시 주의

3. **모델 선택**:
   - 현재는 `gpt-5-nano`를 하드코딩
   - 향후 사용자가 모델을 선택할 수 있도록 확장 가능 (gpt-5-mini, gpt-5 등)

4. **프롬프트 최적화**:
   - 현재 프롬프트는 일반적인 기술 문서용
   - 특정 도메인(의학, 법률 등)에는 추가 튜닝 필요할 수 있음

5. **하위 호환성**:
   - `openai` 패키지가 없어도 기존 기능은 정상 작동해야 함
   - 선택적 import와 fallback 로직으로 보장

---

## 사용자가 해야 할 일

1. **OpenAI API 키 발급**
   - https://platform.openai.com/api-keys 방문
   - "Create new secret key" 클릭
   - 생성된 키를 복사 (`sk-proj-...` 형식)

2. **.env 파일에 API 키 추가**
   - 프로젝트 루트(`c:\github\docling-translate\`)에 `.env` 파일 생성
   - 다음 내용 추가:
     ```bash
     OPENAI_API_KEY=sk-proj-...
     ```
   - 주의: `.env` 파일은 이미 `.gitignore`에 등록되어 있어 Git에 커밋되지 않음

3. **openai 패키지 설치**
   ```bash
   pip install openai
   ```
   - 또는 `requirements.txt`에 이미 추가되어 있으므로:
     ```bash
     pip install -r requirements.txt
     ```

4. **계획 리뷰 및 승인**
   - 이 계획 파일을 검토하고 승인

5. **구현 후 테스트**
   - 번역 품질 확인 (Google vs Gemini vs OpenAI 비교)
   - 필요시 프롬프트 개선 제안

---

*계획 작성일: 2025-11-27*

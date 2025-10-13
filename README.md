# docling-translate

**기술 PDF, 이제 원문과 번역문을 한 문장씩 비교하며 완벽하게 이해하세요.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

`docling-translate`는 비영어권 학생, 엔지니어, 연구원들이 기술 PDF 문서를 손쉽게 읽고 이해할 수 있도록 돕는 빠르고 직관적인 오픈소스 번역 도구입니다.

---

## 🤔 왜 `docling-translate`를 사용해야 할까요?

기술 문서를 번역할 때 이런 어려움, 없으셨나요?

*   📄 PDF 내용을 복사하면 서식이 깨져 번역기에 붙여넣기조차 힘들어요.
*   😵 기존 번역기는 문맥 없는 어색한 결과물만 보여줘서 신뢰하기 어려워요.
*   📑 원문과 번역문을 번갈아 보느라 시간을 낭비하고, 흐름을 놓치기 일쑤예요.

`docling-translate`는 **`docling` 라이브러리**의 강력한 문서 분석 능력과 **문장 단위 병렬 보기**를 결합하여 이 모든 문제를 해결합니다.

## ✨ 핵심 기능

| 기능 | 설명 |
| :--- | :--- |
| **📖 문장 단위 원문-번역 대조** | 원문과 번역문을 한 문장씩 나란히 비교하며, 기술 용어의 미묘한 뉘앙스까지 정확하게 파악할 수 있습니다. |
| **🏗️ 완벽한 PDF 구조 분석** | `docling` 라이브러리를 통해 다단, 표, 이미지 등 복잡한 레이아웃을 정확하게 해석하고 원본 구조를 최대한 유지합니다. |
| **📄 3가지 유연한 출력** | 원문(`_en.md`), 번역문(`_ko.md`), 그리고 원문과 번역문이 병기된 통합본(`_combined.md`)을 모두 생성하여 필요에 맞게 활용할 수 있습니다. |
| **🏷️ 빠른 원문 참조** | 모든 텍스트 블록 옆에 원본 PDF의 페이지 번호 `(p. N)`를 표시하여, 원문을 빠르게 찾아볼 수 있습니다. |

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 사용법

아래 명령어로 PDF 파일을 번역해 보세요.

```bash
python main.py "path/to/your/document.pdf"
```

### 🎨 출력 예시

번역 결과물(`_combined.md`)은 아래와 같이 원문과 번역문이 한 문장 단위로 생성되어, 비교하며 읽기 매우 편리합니다.

---
**Original (English)** (p. 1)
> This assignment marks the foundation of your project journey, so please complete it thoroughly and thoughtfully.

**Translated (Korean)** (p. 1)
> 이 과제는 프로젝트 여정의 기초를 마련하는 것이므로 철저하고 신중하게 완료하십시오.
***
**Original (English)** (p. 1)
> List at least 3–5 planned features and system requirements.

**Translated (Korean)** (p. 1)
> 최소 3~5개의 계획된 기능과 시스템 요구사항을 나열하십시오.
---

## 🗺️ 개발 로드맵

- [x] **PDF → Markdown 변환**: `docling`을 사용한 정확한 구조 분석
- [x] **3가지 포맷 출력**: 원문/번역문/통합본 마크다운 파일 생성
- [x] **페이지 번호 표시**: `(p. N)` 형식으로 원본 페이지 번호 참조
- [x] **문장 단위 번역 및 대조**: 가독성 높은 비교를 위한 문장 단위 번역 (완료!)
- [ ] **폴더 단위 번역**: 단일 파일이 아닌 폴더 전체의 PDF를 한 번에 번역하는 기능
- [ ] **성능 향상을 위한 병렬 처리**: 멀티프로세싱을 활용한 대용량 문서 번역 속도 개선
- [ ] **다중 번역 엔진 지원**: GPT API, 로컬 LLM 등 최신 번역 엔진 선택 기능

## 📚 개발 참고 자료

이 프로젝트는 `docling` 라이브러리를 핵심으로 사용합니다.

*   **`docling` 공식 문서:** 기능과 사용법을 이해하기 위한 가장 중요한 자료입니다.
    *   **GitHub Repository & Docs:** [https://github.com/docling-project/docling/tree/main/docs](https://github.com/docling-project/docling/tree/main/docs)
    *   `@docling-docs/examples` 내의 예제들은 주요 기능 구현에 큰 도움이 됩니다.

## 🤝 기여하기 (Contributing)

여러분의 모든 기여를 환영합니다! 새로운 기능 제안, 버그 수정, 개선 아이디어가 있다면 언제든지 참여해 주세요.

1.  [GitHub Issues](https://github.com/your-username/docling-translate/issues)에 이슈를 등록하여 아이디어를 논의합니다.
2.  이 저장소를 Fork한 후, 변경 사항을 적용하여 Pull Request를 보내주세요.

## 📜 라이선스

이 프로젝트는 **Apache License 2.0** 라이선스를 따릅니다. 자세한 내용은 `LICENSE` 파일을 참고하세요.
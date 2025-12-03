# Issue #55: 문서 구조 재정비 및 ReadTheDocs 통합 (Sphinx) - 한글화

## 목표

사용자의 요청에 따라 모든 문서를 **한국어**로 통일합니다. 또한, 추후 다국어 지원(영어/한국어 전환)을 위한 기반을 마련합니다.

## 배경

현재 문서는 영어(새로 생성된 파일)와 한국어(기존 파일)가 혼재되어 있어 가독성이 떨어집니다. 사용자는 한국어 문서를 선호하며, 추후 언어 전환 기능도 고려하고 있습니다.

## 제안 변경 사항

### 1. 문서 한글화

다음 파일들의 내용을 한국어로 번역하여 수정합니다.

#### [MODIFY] [docs/index.md](file:///c:/github/docling-translate/docs/index.md)
- 제목 및 소개글 한글화

#### [MODIFY] [docs/about.md](file:///c:/github/docling-translate/docs/about.md)
- 프로젝트 소개, 미션, 주요 기능 한글화

#### [MODIFY] [docs/getting_started.md](file:///c:/github/docling-translate/docs/getting_started.md)
- 설치 방법, 필수 조건 한글화

#### [MODIFY] [docs/technical_overview.md](file:///c:/github/docling-translate/docs/technical_overview.md)
- 아키텍처, 기술 스택 설명 한글화

#### [MODIFY] [docs/api_reference.md](file:///c:/github/docling-translate/docs/api_reference.md)
- API 설명 한글화

#### [MODIFY] [docs/configuration.md](file:///c:/github/docling-translate/docs/configuration.md)
- 설정 가이드 한글화

#### [MODIFY] [docs/maintenance.md](file:///c:/github/docling-translate/docs/maintenance.md)
- 유지보수 및 문제 해결 가이드 한글화

#### [MODIFY] [docs/faq.md](file:///c:/github/docling-translate/docs/faq.md)
- 자주 묻는 질문 한글화

#### [MODIFY] [docs/release_notes.md](file:///c:/github/docling-translate/docs/release_notes.md)
- 릴리즈 노트 한글화

### 2. 다국어 지원 (i18n) 준비 (Sphinx-intl)

Sphinx는 `sphinx-intl`을 통해 다국어 문서를 지원합니다. "버튼 눌러서 영어로 읽기" 기능을 구현하려면 다음 단계가 필요합니다.

1.  **기본 언어 설정**: `conf.py`에서 `language = 'ko'`로 설정.
2.  **번역 파일 생성**: `gettext` 빌더를 사용하여 `.pot` 파일 생성 후, 영어(`en`)용 `.po` 파일 생성.
3.  **ReadTheDocs 설정**: ReadTheDocs 대시보드에서 'Translations' 설정을 통해 언어별 버전을 연결해야 함.

**이번 단계에서는 우선 문서 내용을 한국어로 통일하는 것에 집중하고, i18n 설정은 `conf.py`에 기본 언어 설정만 추가하는 것으로 진행합니다.** (완벽한 i18n 구현은 번역 작업량이 2배가 되므로, 일단 한국어판 완성을 우선시합니다.)

#### [MODIFY] [docs/conf.py](file:///c:/github/docling-translate/docs/conf.py)
- `language = 'ko'` 추가

---

## 검증 계획

### 1. 로컬 빌드 테스트

```bash
sphinx-build -b html docs/ docs/_build/html
```

- `docs/_build/html/index.html`을 열어 모든 내용이 자연스러운 한국어로 되어 있는지 확인.

### 2. 검증 체크리스트

- [ ] 모든 페이지가 한국어로 번역되었는가?
- [ ] 기술 용어가 적절하게 사용되었는가?
- [ ] 링크가 깨지지 않고 잘 연결되는가?

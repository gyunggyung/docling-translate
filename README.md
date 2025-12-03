# Docling Translate - GitHub Pages Website

이 브랜치(`gh-pages`)는 **Docling Translate** 프로젝트의 공식 웹사이트 소스 코드를 담고 있습니다.

---

## 🔗 주요 링크

- **공식 웹사이트**: [https://gyunggyung.github.io/docling-translate/](https://gyunggyung.github.io/docling-translate/)
- **공식 문서 (ReadTheDocs)**: [https://docling-translate.readthedocs.io/ko/latest/](https://docling-translate.readthedocs.io/ko/latest/)
- **GitHub 저장소 (main)**: [https://github.com/gyunggyung/docling-translate](https://github.com/gyunggyung/docling-translate)

---

## 📊 현재 상태 (2025-12-03)

### ✅ 정상 작동 중
- **Homepage**: 프리미엄 다크 모드 디자인 적용, CSS 정상 로드
- **기능 소개**: 6개 Feature 카드 (문장 단위 병렬 번역, 다양한 포맷, 레이아웃 보존 등)
- **ReadTheDocs 문서**: 10개 필수 페이지 모두 존재
- **디자인**: Glassmorphism, 애니메이션, 그라데이션 효과 구현

### ⚠️ 현재 문제점
- **Community 페이지**: 존재하지만 navigation bar에 링크 없음
- **Contact 페이지**: 존재하지만 navigation bar에 링크 없음
- **Jekyll Liquid 템플릿 공백 이슈**: `_layouts/default.html`에서 CSS 경로에 공백이 반복적으로 생김 (수정 후에도 다시 발생)

### 🔄 최근 작업 이력
1. **CSS 경로 수정**: Liquid 템플릿의 공백 제거 시도 → 성공 후 다시 공백 발생
2. **Community/Contact 페이지 생성 시도**: HTML 형식으로 생성 → Jekyll 빌드 실패 (404 에러)
3. **긴급 롤백**: 커밋 `26de9e3`로 롤백하여 안정적인 상태로 복구

---

## ✅ Deliverable 03 충족 현황

### Part 1: Documentation (ReadTheDocs) - **완료** ✅

| 필수 페이지 | 상태 |
|-----------|------|
| 1. About the Project | ✅ |
| 2. Getting Started | ✅ |
| 3. How to Use | ✅ |
| 4. Technical Overview | ✅ |
| 5. API Reference | ✅ |
| 6. Configuration Guide | ✅ |
| 7. Maintenance and Troubleshooting | ✅ |
| 8. Contribution Guidelines | ✅ |
| 9. FAQ | ✅ |
| 10. Release Notes | ✅ |

- ✅ docs 폴더에 모두 커밋됨 (main 브랜치)
- ✅ ReadTheDocs 호스팅 연결 완료
- ✅ README에 문서 링크 포함

### Part 2: Website (GitHub Pages) - **대부분 완료** 🔄

| 요구사항 | 상태 |
|---------|------|
| Homepage with mission statement | ✅ |
| Links to Documentation | ✅ |
| Links to GitHub | ✅ |
| Feature Showcase | ✅ |
| Community Section | ⚠️ 페이지 존재하나 nav 링크 없음 |
| Contact Information | ⚠️ 페이지 존재하나 nav 링크 없음 |
| Custom Theme | ✅ 프리미엄 커스텀 디자인 |

### Extra Points
- ✅ **완전 커스텀 Jekyll 테마** (Glassmorphism, 애니메이션, 그라데이션)

---

## 📝 앞으로 해야 할 일

### 🔴 긴급 (Deliverable 03 완성을 위해)

1. **Community 페이지 완성**
   - [ ] `community.md` 파일 수정 (Markdown 형식 사용)
   - [ ] 실제 작동하는 링크 추가:
     - GitHub Discussions
     - GitHub Issues
     - Contribution Guidelines
   - [ ] Navigation bar에 링크 추가 (`_layouts/default.html`)

2. **Contact 페이지 완성**
   - [ ] `contact.md` 파일 수정 (Markdown 형식 사용)
   - [ ] 연락 정보 추가:
     - Email: newhiwoong@gmail.com
     - GitHub Profile: @gyunggyung
     - GitHub Issues (기술 지원)
   - [ ] Navigation bar에 링크 추가

3. **Jekyll Liquid 템플릿 공백 문제 해결**
   - [ ] `_layouts/default.html`의 CSS 경로 공백이 왜 계속 생기는지 원인 파악
   - [ ] 근본적인 해결책 적용

### 🟡 중요 (품질 향상)

4. **콘텐츠 최신화**
   - [ ] `index.md`의 Feature 설명이 실제 프로젝트 기능과 일치하는지 검증
   - [ ] 각 섹션의 링크가 모두 작동하는지 확인

5. **SEO 최적화**
   - [ ] 메타 태그 추가 (description, keywords)
   - [ ] Open Graph 태그 추가
   - [ ] sitemap.xml 생성

### 🟢 선택 (추가 개선)

6. **추가 페이지**
   - [ ] Features 상세 페이지
   - [ ] 사용 사례 (Use Cases) 페이지

7. **로컬 Jekyll 실행 환경 구축**
   - [ ] Ruby/Jekyll 설치
   - [ ] 로컬에서 빌드 테스트 가능하게 설정
   - [ ] Python HTTP 서버 대신 실제 Jekyll 서버 사용

---

## 🛠️ 기술 스택

- **Static Site Generator**: Jekyll
- **Hosting**: GitHub Pages
- **Documentation**: Sphinx + ReadTheDocs
- **Theme**: Custom (Glassmorphism + Dark Mode)
- **Fonts**: Pretendard, Outfit, JetBrains Mono
- **CSS Features**: Animations, Gradients, Backdrop Blur

---

## ⚠️ 주의사항

### Jekyll + Markdown 작업 시
1. **Markdown 형식 유지**: `layout: default`와 함께 순수 Markdown 콘텐츠 사용
2. **permalink 필수**: `/community/`, `/contact/` 같은 경로 지정
3. **HTML 직접 사용 피하기**: Jekyll이 처리하지 못함

### Git 작업 시
1. **gh-pages 브랜치**: 웹사이트 전용 브랜치
2. **main 브랜치**: 프로젝트 소스 코드 및 docs 폴더
3. **강제 push 주의**: 필요시에만 `-f` 옵션 사용

### GitHub Pages 빌드
- 빌드 시간: push 후 1-2분 소요
- 빌드 로그: GitHub Actions 탭에서 확인
- 404 에러 발생 시: Jekyll 빌드 실패 가능성 높음

---

## 📞 연락처

- **Email**: newhiwoong@gmail.com
- **GitHub**: [@gyunggyung](https://github.com/gyunggyung)
- **Issues**: [프로젝트 이슈](https://github.com/gyunggyung/docling-translate/issues)

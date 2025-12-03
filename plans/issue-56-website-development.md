# Issue-56: 웹사이트 구축 (GitHub Pages + Jekyll)

## 1. 목표 (Goal)
- **GitHub Pages**와 **Jekyll**을 사용하여 프로젝트 공식 웹사이트를 구축합니다.
- 과제 요구사항(Deliverable 03 - Part 2)을 충족하는 구조와 콘텐츠를 포함합니다.
- ReadTheDocs 문서 및 GitHub 저장소와의 유기적인 연결을 제공합니다.

## 2. 배경 (Background)
- 현재 `docling-translate` 프로젝트는 기능 구현과 문서화(Part 1)가 완료된 상태입니다.
- 사용자 접근성을 높이고 커뮤니티 활성화를 위해 공식 웹사이트(Part 2)가 필요합니다.
- Apache Hadoop 웹사이트나 Django Community 페이지와 같은 전문적인 오픈소스 프로젝트 웹사이트를 지향합니다.

## 3. 요구사항 (Requirements)
### 필수 요건 (Mandatory)
- **기술 스택**: GitHub Pages, Jekyll.
- **테마**: Jekyll 테마 사용 (커스텀 테마 제작 시 가산점 - *시간 허용 시 고려*).
- **필수 페이지 및 섹션**:
    1.  **🏠 Homepage**:
        -   매력적인 미션 선언문 (Mission Statement).
        -   ReadTheDocs(Live Docs) 및 GitHub 저장소로 가는 직관적인 링크.
        -   Apache Hadoop 웹사이트 스타일의 시각적 영감 반영.
    2.  **✨ Feature Showcase**:
        -   프로젝트의 핵심 기능과 장점 강조 (다양한 포맷, 로컬 LLM, 인터랙티브 뷰어 등).
    3.  **👥 Community Section**:
        -   Django Community 스타일의 커뮤니티 페이지.
        -   Discussion Forums (GitHub Discussions 링크).
        -   Mailing Lists (Google Groups 등 예시 링크 또는 실제 생성).
        -   Communication Channels (Slack/Discord 링크).
    4.  **📬 Contact Information**:
        -   이메일, 연락처 폼, 또는 소셜 미디어 링크.

### 통합 (Integration)
- 웹사이트 내에서 Documentation(ReadTheDocs), GitHub Repository, Community Channels로의 라이브 링크 제공.

## 4. 구현 계획 (Implementation Plan)

### 단계 1: Jekyll 환경 설정 (Setup)
- [ ] `website/` 디렉토리 생성.
    - *전략*: `main` 브랜치 내에 `website/` 폴더를 만들고, 여기에 Jekyll 소스를 둡니다.
    - GitHub Pages 배포 시 "Source" 설정을 조정하거나, GitHub Actions를 사용하여 `website/` 폴더의 내용을 배포하도록 설정합니다.
- [ ] Jekyll 테마 선정 및 설치.
    - 후보: `minima` (기본).
    - `website/` 폴더 안에서 `jekyll new .` 명령어로 초기화.

### 단계 2: 콘텐츠 작성 (Content Creation)
- [ ] `_config.yml`: 사이트 설정 (제목, 설명, 링크 등).
- [ ] `index.md` (Homepage): 미션, 배너, 주요 링크 버튼.
- [ ] `features.md`: 기능 소개 (스크린샷, GIF 활용).
- [ ] `community.md`: 커뮤니티 가이드라인 및 링크 모음.
- [ ] `contact.md`: 연락처 정보.

### 단계 3: 디자인 및 스타일링 (Design & Styling)
- [ ] CSS/SCSS 커스터마이징: 프로젝트 브랜드 컬러(파란색 계열?) 적용.
- [ ] 반응형 레이아웃 확인.

### 단계 4: 배포 및 연동 (Deployment)
- [ ] GitHub Repository 설정: Pages 소스를 `gh-pages` 브랜치로 설정.
- [ ] ReadTheDocs 및 GitHub 링크 연결 확인.

## 5. 검증 계획 (Verification Plan)
### 자동화 테스트
- [ ] 로컬 Jekyll 빌드 (`bundle exec jekyll serve`) 성공 여부.

### 수동 검증
- [ ] 모든 링크(ReadTheDocs, GitHub, Community)가 정상 작동하는지 확인.
- [ ] 모바일 및 데스크탑 환경에서 레이아웃 깨짐 없는지 확인.

## 6. 예상되는 효과 (Expected Outcome)
- 전문적인 오픈소스 프로젝트로서의 신뢰도 상승.
- 사용자가 프로젝트 정보를 한눈에 파악하고 문서나 커뮤니티로 쉽게 이동 가능.
- 과제 요구사항 완벽 충족.

# Issue #82: Add Demo Assets to README

## 목표

새로 추가된 데모 비디오(`demo.mp4`)와 이미지 자산을 `README.md` 및 `docs/README.en.md`에 추가하여 프로젝트의 시각적 매력을 높이고 사용자가 기능을 직관적으로 이해할 수 있도록 돕습니다.

## 배경

사용자가 `docs/assets/images` 및 `docs/assets/videos/demo.mp4` 경로에 새로운 자산을 추가했습니다. 이를 README에 효과적으로 배치하여 문서를 꾸미고 싶어합니다. 특히 비디오 데모는 사용자가 도구의 작동 방식을 빠르게 파악하는 데 큰 도움이 됩니다.

## 제안 변경 사항

### 문서 (Documentation)

#### [MODIFY] [README.md](file:///c:/github/docling-translate/README.md)

**변경 내용**:
1. **뱃지 개선**:
   - 가독성을 위해 색상을 조정하고 통일감 있게 배치합니다.
   - **GitHub Stars** 뱃지를 추가합니다.
   - 예시:
     - Python: `3776AB`
     - License: `green`
     - English: `red`
     - Discussions: `6524fa`

2. **데모 비디오 및 이미지 추가**:
   - `개요` 섹션 직후에 `docling.png` (5개 파일 처리 이미지)를 배치하여 지원 포맷을 시각적으로 강조합니다.
   - `주요 기능` 섹션 전에 데모 비디오를 삽입합니다.
   - `상세 가이드` 섹션 이전에 `아키텍처 (Architecture)` 섹션을 신설하고 `architecture.png`를 추가합니다.
   - `Community` 또는 문서 하단에 `qr.png`를 배치하여 모바일 접근성을 높이거나 홍보용으로 사용합니다.

**핵심 코드 (이미지 및 비디오)**:
```markdown
## 개요

... (기존 텍스트)

<p align="center">
  <img src="docs/assets/images/docling.png" alt="Supported Formats" width="80%">
</p>

...

## 데모 (Demo)

<p align="center">
  <video src="docs/assets/videos/demo.mp4" controls="controls" style="max-width: 100%;">
  </video>
</p>

...

## 아키텍처 (Architecture)

<p align="center">
  <img src="docs/assets/images/architecture.png" alt="Architecture Diagram" width="100%">
</p>

...

## Community & Support

<p align="center">
  <img src="docs/assets/images/qr.png" alt="Join Community" width="200px">
</p>
```

---

#### [MODIFY] [README.en.md](file:///c:/github/docling-translate/docs/README.en.md)

**변경 내용**:
- `README.md`와 동일하게 뱃지, 데모 비디오, 아키텍처 다이어그램, QR 코드를 추가합니다.
- 이미지 및 비디오 경로는 `assets/images/` 및 `assets/videos/` (상대 경로)로 조정합니다.

## 검증 계획

### 1. 육안 검사
- 로컬 마크다운 뷰어 또는 GitHub 프리뷰를 통해 모든 이미지가 깨지지 않고 로드되는지 확인합니다.
- 뱃지 색상이 의도대로 나오는지 확인합니다.
- 상대 경로가 각 README 파일 위치에서 올바른지 확인합니다.

### 2. 검증 체크리스트
- [ ] `docling.png`가 개요 부분에 잘 보이는가?
- [ ] `architecture.png`가 아키텍처 섹션에 적절한 크기로 들어갔는가?
- [ ] `qr.png`가 적절한 위치(하단 등)에 배치되었는가?
- [ ] `README.md`에서 비디오/이미지 경로가 `docs/assets/...`로 올바른가?
- [ ] `docs/README.en.md`에서 비디오/이미지 경로가 `assets/...`로 올바른가?
- [ ] Stars 뱃지 및 컬러 뱃지가 적용되었는가?

## 예상 효과

- **사용성**: 사용자가 설치 전에 실제 작동 모습을 영상을 통해 미리 확인할 수 있어 진입 장벽이 낮아집니다.
- **심미성**: 텍스트 위주의 문서에 시각적 요소가 더해져 프로젝트의 완성도가 높아 보입니다.

# [Issue] 데모 비디오 GIF로 교체

## 목표
`README.md` 및 `docs/README.en.md`에서 정상적으로 재생되지 않는 `demo.mp4` `<video>` 태그를 `demo.gif`를 사용하는 `<img>` 태그로 교체합니다.

## 사용자 질문 답변
**사용자 질문:** "`docs/assets/videos` 폴더 이름을 바꿔야 할까요? `img`로 통합할까요? 아니면 그대로 둘까요?"
**답변:** **`docs/assets/videos` 그대로 유지하는 것을 추천합니다.**
1.  **의미적 명확성:** 움직이는 영상(GIF, MP4)은 `videos`에, 정적인 스크린샷은 `images`에 두는 것이 나중에 파일을 찾기 더 쉽습니다.
2.  **기존 구조 유지:** 이미 폴더와 파일이 존재하므로, 굳이 이름을 변경하여 경로를 수정하는 불필요한 작업을 할 필요가 없습니다.
3.  **확장성:** 나중에 YouTube 링크나 고화질 MP4 다운로드 링크를 추가할 경우, 이 폴더가 가장 적합한 위치입니다.

## 변경 제안

### 문서 (Documentation)

#### [MODIFY] [README.md](file:///c:/github/docling-translate/README.md)
*   `<video>` 태그 블록을 `docs/assets/videos/demo.gif`를 가리키는 `<img>` 태그로 교체합니다.

#### [MODIFY] [README.en.md](file:///c:/github/docling-translate/docs/README.en.md)
*   `<video>` 태그 블록을 `assets/videos/demo.gif`를 가리키는 `<img>` 태그로 교체합니다.

## 검증 계획

### 수동 검증
1.  **육안 확인:** `README.md` 및 `docs/README.en.md` 파일의 마크다운 문법이 올바른지 확인합니다.
2.  **미리보기:** (가능한 경우) 마크다운 미리보기를 통해 이미지가 정상적으로 로드되는지 확인합니다.

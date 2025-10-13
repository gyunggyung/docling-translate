# 기여 가이드라인

`docling-translate`에 기여하는 데 관심을 가져주셔서 감사합니다! 버그 리포트부터 새로운 기능 추가까지 모든 기여를 환영합니다. 원활하고 협력적인 과정을 위해, 우리는 GitHub Flow 워크플로우를 따릅니다.

## 개발 워크플로우 (GitHub Flow)

핵심 원칙은 `main` 브랜치가 항상 안정적이고 배포 가능한 상태여야 한다는 것입니다. 모든 새로운 작업은 별도의 브랜치에서 수행됩니다.

### 1단계: 이슈 생성

작업을 시작하기 전, 먼저 [이슈(issue)](https://github.com/gyunggyung/docling-translate/issues)를 생성하여 해결하려는 버그, 추가하려는 기능, 또는 개선점에 대해 논의해주세요. 이를 통해 다른 사람들과 논의하고, 작업 방향이 프로젝트의 목표와 일치하는지 확인할 수 있습니다.

### 2단계: 브랜치 생성

이슈가 정해지면, `main` 브랜치에서 새로운 브랜치를 만듭니다. 브랜치 이름은 아래 규칙에 따라 작업 내용을 잘 설명하도록 지어주세요.

*   새로운 기능: `feat/<description>` (예: `feat/add-multi-language-support`)
*   버그 수정: `fix/<description>` (예: `fix/pdf-parsing-error`)
*   문서 작업: `docs/<description>` (예: `docs/update-contributing-guide`)

```bash
# main 브랜치로 이동하여 최신 버전으로 업데이트합니다.
git checkout main
git pull origin main

# 새로운 브랜치를 생성합니다.
git checkout -b feat/your-feature-name
```

### 3단계: 개발 및 커밋

새로 만든 브랜치에서 변경사항을 만들고, 작업한 내용을 설명하는 명확한 메시지와 함께 작고 논리적인 단위로 커밋해주세요.

```bash
# 변경사항을 스테이징합니다.
git add .

# 변경사항을 커밋합니다.
git commit -m "feat: Add support for Spanish translation"
```

### 4단계: 풀 리퀘스트(PR) 생성

작업이 끝나 리뷰받을 준비가 되면, 브랜치를 GitHub에 푸시하고 `main` 브랜치로 Pull Request(PR)를 생성합니다.

```bash
# 원격 저장소에 브랜치를 푸시합니다.
git push origin feat/your-feature-name
```

그 다음, `docling-translate` GitHub 저장소 페이지로 이동하면 당신의 브랜치로 PR을 생성하라는 안내가 보일 것입니다. PR에 명확한 제목과 상세한 설명을 작성하고, 관련 있는 이슈를 링크해주세요 (예: "Closes #123").

### 5단계: 코드 리뷰 (선택적)

PR이 생성되면, 다른 기여자(또는 AI 에이전트)가 코드를 리뷰합니다. 이는 코드의 품질, 일관성, 정확성을 보장하기 위한 협업 과정입니다. 특히 중요한 코드 변경의 경우 리뷰를 거치는 것을 권장하지만, 오타 수정과 같은 간단한 문서 변경에는 이 단계를 건너뛸 수 있습니다.

피드백에 열린 자세를 유지하고, 요청 시 추가적인 변경사항을 적용할 준비를 해주세요.

### 6단계: 병합 (Merge)

PR이 리뷰를 통과하고 승인되면, 프로젝트 관리자가 `main` 브랜치에 병합합니다. 이제 당신의 기여가 프로젝트의 일부가 되었습니다!

`docling-translate`를 더 나은 프로젝트로 만들어주셔서 감사합니다!

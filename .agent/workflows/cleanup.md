---
description: 작업 브랜치를 정리하고 main 브랜치를 최신화합니다
---
// turbo-all

1. main 브랜치로 이동하고 원격 저장소 내용을 당겨옵니다
   ```bash
   git checkout main
   git pull origin main
   ```

2. 작업 브랜치를 삭제합니다 (필요한 경우 브랜치명을 지정하세요)
   ```bash
   git branch -d <branch_name>
   ```

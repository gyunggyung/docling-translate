# Issue #57: Restore Progress Bar & Granular Status

## 목표

Streamlit 웹 UI에서 문서 번역 진행 상황을 실시간으로 시각화하고, 각 단계별 상세 상태 메시지를 표시하여 사용자 경험을 개선합니다. 특히 병렬 번역 시 진행률이 멈춰 보이는 문제를 해결합니다.

## 배경

모듈화 작업 이후 `src/translation/base.py`의 병렬 처리 로직이 `executor.map`을 사용하게 되면서, 번역이 완료될 때까지 진행률 업데이트가 되지 않는 문제가 발생했습니다. 또한 `src/core.py`의 단계별 상태 메시지가 UI에 충분히 전달되지 않고 있습니다.

## 제안 변경 사항

### 1. 병렬 번역 진행률 개선

#### [MODIFY] [src/translation/base.py](file:///c:/github/docling-translate/src/translation/base.py)

**변경 내용**:
- `translate_batch` 메서드에서 `executor.map` 대신 `executor.submit`과 `as_completed` 패턴을 사용하도록 변경합니다.
- 각 작업이 완료될 때마다 `progress_cb`를 호출하여 실시간 진행률을 업데이트합니다.
- `future` 객체와 원본 인덱스를 매핑하여, 번역 완료 후 원래 문장 순서대로 결과를 재정렬합니다.

**핵심 코드**:
```python
# 변경 후 (개념)
futures = {executor.submit(self.translate, s, src, dest): i for i, s in enumerate(sentences)}
results = [None] * len(sentences)

for i, future in enumerate(concurrent.futures.as_completed(futures)):
    idx = futures[future]
    results[idx] = future.result() or ""
    if progress_cb:
        progress_cb((i + 1) / total, f"번역 중... ({i + 1}/{total})")
```

### 2. 단계별 상태 메시지 세분화 및 "실제 실행 시간" 반영

#### [MODIFY] [src/core.py](file:///c:/github/docling-translate/src/core.py)

**변경 내용**:
- **진행률 가중치 현실화**: 실제 소요 시간을 반영하여 가중치를 조정합니다.
    - **문서 구조 분석 (Docling)**: 20% (블로킹 작업)
    - **텍스트 추출**: 5%
    - **번역 (Translation)**: 60% (가장 오래 걸림, 실시간 업데이트)
    - **결과 생성 및 이미지 저장**: 15% (이미지 저장 포함)
- **상세 상태 메시지 적용**:
    - 시작 시: "📄 문서 구조 분석 및 변환 중..."
    - 변환 후: "📝 텍스트 및 캡션 추출 중..."
    - 번역 중: "🤖 번역 중... (진행률: N/Total)"
    - HTML 생성 진입: "💾 결과 파일 생성 및 이미지 저장 중..."
    - 완료: "✅ 모든 작업 완료!"

#### [MODIFY] [src/html_generator.py](file:///c:/github/docling-translate/src/html_generator.py)

**변경 내용**:
- `generate_html_content` 함수에 `progress_cb` 파라미터를 추가합니다.
- HTML 생성 루프 내에서 이미지(`TableItem`, `PictureItem`)를 저장할 때마다 진행률을 업데이트합니다.
- 메시지 예시: "🖼️ 이미지 저장 중... (3/10)"

### 3. UI 연동 확인

#### [MODIFY] [app.py](file:///c:/github/docling-translate/app.py)

**변경 내용**:
- `process_document` 호출 시 전달하는 `update_progress` 콜백이 `src/core.py`에서 전달하는 메시지를 그대로 화면에 표시하도록 확인 및 미세 조정합니다.

---

## 검증 계획

### 1. 수동 테스트

**시나리오 1: 대량 문서 번역 테스트**
- 단계:
  1. 페이지가 많은 PDF (또는 텍스트가 많은 문서)를 업로드합니다.
  2. "새로 번역 시작" 버튼을 클릭합니다.
  3. 진행률 바가 멈추지 않고 꾸준히 올라가는지 확인합니다.
  4. 상태 메시지가 "문서 변환 중...", "텍스트 수집 중...", "번역 중... (10/100)", "HTML 생성 중..." 등으로 실시간 변경되는지 확인합니다.
- 예상 결과: 진행률 바와 텍스트가 작업 흐름에 맞춰 부드럽게 갱신되어야 합니다.

### 2. 검증 체크리스트

- [ ] 병렬 번역 시 진행률이 실시간으로 올라가는가?
- [ ] 번역 완료 후 문장 순서가 뒤섞이지 않고 원본과 일치하는가?
- [ ] UI에 표시되는 상태 메시지가 사용자 친화적인가?

---

## 예상 효과

- **사용성**: 사용자가 작업이 멈춘 것으로 오해하지 않고, 현재 어떤 작업이 진행 중인지 명확히 알 수 있어 불안감이 해소됩니다.
- **품질**: 사용자에게 더 전문적이고 완성도 높은 서비스 경험을 제공합니다.

---

## 주의사항

- `as_completed` 사용 시 순서 보장을 위해 인덱스 매핑 로직을 신중하게 구현해야 합니다.
- 너무 잦은 콜백 호출(예: 문장 1개마다 UI 갱신)은 오버헤드가 될 수 있으므로, 필요 시 일정 간격(예: 10개 단위)으로 갱신하도록 조절을 고려합니다. (일단은 실시간 갱신으로 구현)

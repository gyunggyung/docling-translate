# Issue #28 – Web UI 이미지·표 표시 문제

## 실제 문제
- main.py 에서는 정상적으로 번역이 잘 됨.
- app.py 에서는 텍스트 번역은 잘 되나 이미지 및 표를 저장하지 않음.
- 따라서 http://localhost:8501/ 웹 UI에서 이미지·표가 보이지 않음.
- main.py를 참고해서 app.py에서도 이미지 표가 잘 저장되도록 수정.
- 이 아래 모든 내용은 GPT-OSS 120B가 적은 것. 실제 해결 방법이 아닐 수도 있으니 참고만 하길 바람.

## 문제 요약
- `app.py`에서 번역 결과 HTML을 표시할 때 이미지(`PictureItem`)와 표(`TableItem`)가 **보이지 않음**.
- `main.py`는 `save_and_get_image_path`를 통해 `output/<folder>/images/`에 파일을 저장하고, HTML에 `src="images/..."` 경로를 삽입하지만, 웹 UI는 로컬 파일을 직접 로드할 수 없어 이미지가 사라진다.

## 원인 분석
1. **이미지·표 경로 변환 누락**
   - 배치 결과와 단일 결과 모두 `inject_images` 함수를 호출하지 않아 `src="images/..."`가 그대로 남아 있다.
2. **`inject_images` 사용 위치**
   - 기존 코드에서는 배치 결과 `subtab1`과 단일 결과 `tab1`에서 HTML을 바로 `components.html`에 전달하고 있었다.

## 해결 방안
1. **`inject_images` 호출 추가**
   - HTML을 읽은 뒤 `inject_images(html_content, output_dir)`를 호출해 이미지·표 경로를 Base64 데이터 URI로 변환한다.
2. **배치 결과와 단일 결과 모두 적용**
   - `subtab1`(배치)와 `tab1`(단일)에서 위 변환 로직을 삽입.
3. **주석 추가**
   - 왜 변환이 필요한지 설명하는 주석을 넣어 유지보수성을 높인다.

## 구현 내용 (핵심 코드 변경)
```python
# 배치 결과 - 인터랙티브 뷰
if html_path.exists():
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    # 이미지·표를 Base64로 변환하여 임베드
    html_content_view = inject_images(html_content, output_dir)
    components.html(html_content_view, height=600, scrolling=True)
```
```python
# 단일 결과 - 인터랙티브 뷰
if html_path.exists():
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    html_content_view = inject_images(html_content, output_dir)
    components.html(html_content_view, height=800, scrolling=True)
```

## 검증 단계
1. `streamlit run app.py` 실행 후 페이지 새로고침(F5).
2. PDF 파일을 업로드하고 번역을 수행.
3. 결과 탭에서 이미지·표가 정상적으로 표시되는지 확인.
4. `output/<folder>/images/`에 이미지 파일이 존재하고, HTML에 `data:image/...;base64,` 형태로 변환된 것을 확인.

## 기대 효과
- 웹 UI에서도 CLI와 동일하게 이미지·표가 표시되어 사용자 경험이 크게 향상.
- `inject_images` 로직을 일관되게 적용해 유지보수 용이.

*작성일: 2025-11-22*

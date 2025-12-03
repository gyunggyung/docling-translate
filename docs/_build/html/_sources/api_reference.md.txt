# API 레퍼런스 (API Reference)

이 섹션은 Docling Translate의 내부 API를 설명합니다. 이 도구는 주로 CLI로 사용되지만, 개발자가 프로젝트를 확장하고자 할 때 유용합니다.

## Converter

### `src.converter.PDFConverter`

```python
class PDFConverter:
    def __init__(self, file_path: str):
        """
        파일 경로를 받아 컨버터를 초기화합니다.
        """
        ...

    def convert(self) -> Document:
        """
        PDF를 구조화된 Document 객체로 변환합니다.
        """
        ...
```

## Translator

### `src.translator.TranslatorEngine`

```python
class TranslatorEngine:
    def translate(self, text: str, target_lang: str = "ko") -> str:
        """
        주어진 텍스트를 목표 언어로 번역합니다.
        """
        ...
```

## HTML Generator

### `src.html_generator.create_html`

```python
def create_html(original: List[str], translated: List[str], output_path: str):
    """
    인터랙티브 HTML 파일을 생성합니다.
    """
    ...
```

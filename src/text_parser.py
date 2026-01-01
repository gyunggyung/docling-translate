"""
src/text_parser.py
==================
텍스트 파일을 파싱하여 번역 대상 영역을 지능적으로 추출하는 모듈입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **파일 타입 감지**: 확장자를 기반으로 파일 타입을 식별합니다.
2.  **세그먼트 추출**: 파일을 번역 가능/불가능 영역으로 분리합니다.
3.  **스마트 파싱**: 마크다운은 코드블록 제외, 코드 파일은 주석만 추출 등

지원 파일 타입:
- 마크다운: .md, .markdown, .rst
- 파이썬: .py (# 주석, triple-quote 독스트링)
- C 계열: .c, .cpp, .h, .java, .cs, .go, .rs, .swift (// 및 /* */ 주석)
- 자바스크립트: .js, .ts, .jsx, .tsx
- 쉘: .sh, .bash (# 주석)
- 설정: .json, .yaml, .yml, .toml (전체 번역)
- 일반 텍스트: .txt, LICENSE 등 (전체 번역)
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
import logging


@dataclass
class TextSegment:
    """
    번역 가능한 텍스트 조각을 나타내는 데이터 클래스입니다.
    
    Attributes:
        text: 원본 텍스트
        start_pos: 파일 내 시작 위치 (문자 인덱스)
        end_pos: 파일 내 끝 위치 (문자 인덱스)
        translatable: 번역 대상 여부
        segment_type: 세그먼트 유형 ('prose', 'comment', 'code', 'docstring', 'header' 등)
        line_number: 시작 줄 번호 (디버깅용)
    """
    text: str
    start_pos: int
    end_pos: int
    translatable: bool
    segment_type: str
    line_number: int = 0


class TextFileParser:
    """
    텍스트 파일을 파싱하여 번역 대상 영역을 추출합니다.
    
    파일 타입별로 다른 파싱 전략을 사용합니다:
    - 마크다운: 코드블록/인라인코드 제외
    - 코드 파일: 주석과 독스트링만 추출
    - 일반 텍스트: 전체 번역
    """
    
    # 파일 확장자 -> 파서 타입 매핑
    EXTENSION_MAP = {
        # 마크다운/문서
        'md': 'markdown',
        'markdown': 'markdown',
        'rst': 'plaintext',  # RST는 일단 전체 번역
        
        # 파이썬
        'py': 'python',
        'pyw': 'python',
        
        # C 스타일 주석 (// 및 /* */)
        'js': 'c_style',
        'jsx': 'c_style',
        'ts': 'c_style',
        'tsx': 'c_style',
        'mjs': 'c_style',
        'cjs': 'c_style',
        'c': 'c_style',
        'h': 'c_style',
        'cpp': 'c_style',
        'hpp': 'c_style',
        'cc': 'c_style',
        'cxx': 'c_style',
        'cs': 'c_style',
        'java': 'c_style',
        'kt': 'c_style',
        'kts': 'c_style',
        'go': 'c_style',
        'rs': 'c_style',
        'swift': 'c_style',
        
        # 쉘 스크립트 (# 주석)
        'sh': 'shell',
        'bash': 'shell',
        'zsh': 'shell',
        'fish': 'shell',
        
        # 설정 파일 (전체 번역)
        'json': 'config',
        'yaml': 'config',
        'yml': 'config',
        'toml': 'config',
        'xml': 'config',
        
        # 일반 텍스트
        'txt': 'plaintext',
        'text': 'plaintext',
        'log': 'plaintext',
        'cfg': 'plaintext',
        'ini': 'plaintext',
        'env': 'plaintext',
    }
    
    def __init__(self):
        """파서 초기화"""
        pass
    
    def parse(self, file_path: Path) -> List[TextSegment]:
        """
        파일을 파싱하여 세그먼트 리스트를 반환합니다.
        
        Args:
            file_path: 파싱할 파일 경로
            
        Returns:
            TextSegment 리스트
        """
        file_path = Path(file_path)
        ext = file_path.suffix.lstrip('.').lower()
        
        # 파서 타입 결정
        parser_type = self.EXTENSION_MAP.get(ext, 'plaintext')
        
        # 확장자가 없는 경우 (LICENSE, README 등)
        if not ext:
            parser_type = 'plaintext'
        
        # 파일 읽기 (인코딩 오류는 무시)
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding='cp949')
            except UnicodeDecodeError:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        logging.info(f"[TextParser] 파일 파싱: {file_path.name} (타입: {parser_type})")
        
        # 파서 타입에 따라 분기
        if parser_type == 'markdown':
            return self._parse_markdown(content)
        elif parser_type == 'python':
            return self._parse_python(content)
        elif parser_type == 'c_style':
            return self._parse_c_style(content)
        elif parser_type == 'shell':
            return self._parse_shell(content)
        elif parser_type == 'config':
            return self._parse_config(content)
        else:
            return self._parse_plaintext(content)
    
    def _parse_markdown(self, content: str) -> List[TextSegment]:
        """
        마크다운 파싱: 코드블록만 분리, 인라인 코드는 포함된 채로 번역
        
        번역 제외 대상:
        - 코드 블록: ```...``` 또는 ~~~...~~~
        
        인라인 코드(`...`)는 텍스트에 포함된 채로 번역 (HTML 렌더링 시 스타일링만)
        """
        segments = []
        pos = 0
        line_number = 1
        
        # 코드 블록 패턴: ```language\n...\n``` 또는 ~~~...~~~
        code_block_pattern = re.compile(r'(```[\w]*\n.*?\n```|~~~[\w]*\n.*?\n~~~)', re.DOTALL)
        
        # 코드 블록 찾기
        for match in code_block_pattern.finditer(content):
            # 코드 블록 이전 텍스트 (번역 대상) - 문단 단위로 분리
            if match.start() > pos:
                before_text = content[pos:match.start()]
                if before_text.strip():
                    # 문단 단위로 분리 (빈 줄 기준)
                    para_segments = self._split_by_paragraphs(before_text, pos, line_number)
                    segments.extend(para_segments)
                line_number += before_text.count('\n')
            
            # 코드 블록 (번역 불가)
            code_text = match.group()
            segments.append(TextSegment(
                text=code_text,
                start_pos=match.start(),
                end_pos=match.end(),
                translatable=False,
                segment_type='code_block',
                line_number=line_number
            ))
            line_number += code_text.count('\n')
            pos = match.end()
        
        # 마지막 텍스트
        if pos < len(content):
            remaining = content[pos:]
            if remaining.strip():
                para_segments = self._split_by_paragraphs(remaining, pos, line_number)
                segments.extend(para_segments)
        
        return segments
    
    def _split_by_paragraphs(self, text: str, start_pos: int, line_number: int) -> List[TextSegment]:
        """
        텍스트를 문단 단위로 분리하여 세그먼트 리스트 반환
        빈 줄(\n\n)을 기준으로 문단 분리
        """
        segments = []
        paragraphs = re.split(r'\n\s*\n', text)
        current_pos = start_pos
        current_line = line_number
        
        for para in paragraphs:
            if para.strip():
                segments.append(TextSegment(
                    text=para.strip(),
                    start_pos=current_pos,
                    end_pos=current_pos + len(para),
                    translatable=True,
                    segment_type='prose',
                    line_number=current_line
                ))
            current_line += para.count('\n') + 2  # 문단 구분자 포함
            current_pos += len(para) + 2
        
        return segments
    
    def _parse_python(self, content: str) -> List[TextSegment]:
        """
        파이썬 파싱: 주석(#)과 독스트링(triple quotes)만 번역
        
        번역 대상:
        - 한 줄 주석: # comment
        - 독스트링: triple single/double quotes (줄 단위 분리)
        """
        segments = []
        pos = 0
        line_number = 1
        
        # 패턴: 독스트링 또는 한 줄 주석
        pattern = re.compile(
            r'("""|\'\'\')([\s\S]*?)(\1)|#[^\n]*',
            re.MULTILINE
        )
        
        for match in pattern.finditer(content):
            # 매치 이전 코드 (번역 불가)
            if match.start() > pos:
                code_text = content[pos:match.start()]
                if code_text.strip():
                    segments.append(TextSegment(
                        text=code_text,
                        start_pos=pos,
                        end_pos=match.start(),
                        translatable=False,
                        segment_type='code',
                        line_number=line_number
                    ))
                line_number += code_text.count('\n')
            
            # 주석 또는 독스트링 (번역 대상)
            comment_text = match.group()
            is_docstring = comment_text.startswith('"""') or comment_text.startswith("'''")
            
            if is_docstring:
                # 독스트링은 줄 단위로 분리하여 가독성 향상
                lines = comment_text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        segments.append(TextSegment(
                            text=line,
                            start_pos=match.start(),
                            end_pos=match.end(),
                            translatable=True,
                            segment_type='docstring',
                            line_number=line_number + i
                        ))
            else:
                # 한 줄 주석
                segments.append(TextSegment(
                    text=comment_text,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    translatable=True,
                    segment_type='comment',
                    line_number=line_number
                ))
            
            line_number += comment_text.count('\n')
            pos = match.end()
        
        # 마지막 코드
        if pos < len(content):
            remaining = content[pos:]
            if remaining.strip():
                segments.append(TextSegment(
                    text=remaining,
                    start_pos=pos,
                    end_pos=len(content),
                    translatable=False,
                    segment_type='code',
                    line_number=line_number
                ))
        
        return segments
    
    def _parse_c_style(self, content: str) -> List[TextSegment]:
        """
        C 스타일 주석 파싱: //, /* */ 주석만 번역
        
        지원 언어: C, C++, Java, C#, JavaScript, TypeScript, Go, Rust, Swift
        
        번역 대상:
        - 한 줄 주석: // comment
        - 여러 줄 주석: /* ... */
        - Rust 문서 주석: /// ...
        """
        segments = []
        pos = 0
        line_number = 1
        
        # 패턴: // 주석, /* */ 여러줄 주석
        pattern = re.compile(
            r'(//[^\n]*|/\*[\s\S]*?\*/)',
            re.MULTILINE
        )
        
        for match in pattern.finditer(content):
            # 매치 이전 코드
            if match.start() > pos:
                code_text = content[pos:match.start()]
                if code_text.strip():
                    segments.append(TextSegment(
                        text=code_text,
                        start_pos=pos,
                        end_pos=match.start(),
                        translatable=False,
                        segment_type='code',
                        line_number=line_number
                    ))
                line_number += code_text.count('\n')
            
            # 주석 (번역 대상)
            comment_text = match.group()
            segment_type = 'block_comment' if comment_text.startswith('/*') else 'line_comment'
            
            segments.append(TextSegment(
                text=comment_text,
                start_pos=match.start(),
                end_pos=match.end(),
                translatable=True,
                segment_type=segment_type,
                line_number=line_number
            ))
            line_number += comment_text.count('\n')
            pos = match.end()
        
        # 마지막 코드
        if pos < len(content):
            remaining = content[pos:]
            if remaining.strip():
                segments.append(TextSegment(
                    text=remaining,
                    start_pos=pos,
                    end_pos=len(content),
                    translatable=False,
                    segment_type='code',
                    line_number=line_number
                ))
        
        return segments
    
    def _parse_shell(self, content: str) -> List[TextSegment]:
        """
        쉘 스크립트 파싱: # 주석만 번역 (shebang 제외)
        
        번역 대상:
        - 주석: # comment (단, #!로 시작하는 shebang 제외)
        """
        segments = []
        pos = 0
        line_number = 1
        
        # 패턴: # 주석 (shebang 제외)
        # shebang: #!/bin/bash 등은 제외
        pattern = re.compile(r'^(?!#!)#[^\n]*', re.MULTILINE)
        
        for match in pattern.finditer(content):
            # 매치 이전 코드
            if match.start() > pos:
                code_text = content[pos:match.start()]
                if code_text.strip():
                    segments.append(TextSegment(
                        text=code_text,
                        start_pos=pos,
                        end_pos=match.start(),
                        translatable=False,
                        segment_type='code',
                        line_number=line_number
                    ))
                line_number += code_text.count('\n')
            
            # 주석 (번역 대상)
            comment_text = match.group()
            segments.append(TextSegment(
                text=comment_text,
                start_pos=match.start(),
                end_pos=match.end(),
                translatable=True,
                segment_type='comment',
                line_number=line_number
            ))
            pos = match.end()
        
        # 마지막 코드
        if pos < len(content):
            remaining = content[pos:]
            if remaining.strip():
                segments.append(TextSegment(
                    text=remaining,
                    start_pos=pos,
                    end_pos=len(content),
                    translatable=False,
                    segment_type='code',
                    line_number=line_number
                ))
        
        return segments
    
    def _parse_config(self, content: str) -> List[TextSegment]:
        """
        설정 파일 파싱: 전체 번역 (키와 값 모두)
        
        지원 형식: JSON, YAML, TOML, XML
        
        주의: 번역 후 파일 구조가 깨질 수 있으므로 사용자에게 경고 필요
        """
        # 전체를 하나의 번역 가능 세그먼트로 처리
        return [TextSegment(
            text=content,
            start_pos=0,
            end_pos=len(content),
            translatable=True,
            segment_type='config',
            line_number=1
        )]
    
    def _parse_plaintext(self, content: str) -> List[TextSegment]:
        """
        일반 텍스트 파싱: 전체 번역
        
        적용 대상: .txt, LICENSE, README (확장자 없음) 등
        """
        # 문단 단위로 분리하여 번역 효율성 향상
        segments = []
        paragraphs = content.split('\n\n')
        pos = 0
        line_number = 1
        
        for para in paragraphs:
            if para.strip():
                segments.append(TextSegment(
                    text=para,
                    start_pos=pos,
                    end_pos=pos + len(para),
                    translatable=True,
                    segment_type='prose',
                    line_number=line_number
                ))
            line_number += para.count('\n') + 2  # 문단 구분자 포함
            pos += len(para) + 2  # \n\n
        
        # 빈 문단은 추가하지 않으므로, 전체가 비어있으면 하나로 처리
        if not segments and content.strip():
            segments.append(TextSegment(
                text=content,
                start_pos=0,
                end_pos=len(content),
                translatable=True,
                segment_type='prose',
                line_number=1
            ))
        
        return segments
    
    def get_translatable_texts(self, segments: List[TextSegment]) -> List[str]:
        """
        세그먼트 리스트에서 번역 대상 텍스트만 추출합니다.
        
        Args:
            segments: TextSegment 리스트
            
        Returns:
            번역 대상 텍스트 리스트
        """
        return [seg.text for seg in segments if seg.translatable and seg.text.strip()]


def is_text_file(file_path: str) -> bool:
    """
    파일이 텍스트 파일인지 확인합니다.
    
    확장자 기반으로 판단하며, 확장자가 없는 경우 바이너리 체크를 수행합니다.
    
    Args:
        file_path: 확인할 파일 경로
        
    Returns:
        텍스트 파일이면 True
    """
    path = Path(file_path)
    ext = path.suffix.lstrip('.').lower()
    
    # 알려진 텍스트 확장자
    if ext in TextFileParser.EXTENSION_MAP:
        return True
    
    # 확장자 없는 파일 (LICENSE, README 등)
    if not ext:
        return not _is_binary(file_path)
    
    return False


def _is_binary(file_path: str) -> bool:
    """
    파일이 바이너리인지 확인합니다.
    
    파일의 처음 8KB를 읽어 null byte가 있으면 바이너리로 판단합니다.
    
    Args:
        file_path: 확인할 파일 경로
        
    Returns:
        바이너리 파일이면 True
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            return b'\x00' in chunk
    except Exception:
        return True  # 읽기 실패 시 바이너리로 취급

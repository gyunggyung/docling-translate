"""
src/translation/base.py
=======================
번역 엔진의 추상 기본 클래스(Abstract Base Class)를 정의하는 모듈입니다.

이 모듈은 다음 기능을 수행합니다:
1.  **인터페이스 정의**: 모든 번역 엔진이 구현해야 할 `translate` 메서드를 정의합니다.
2.  **일괄 번역**: `translate_batch` 메서드를 통해 다중 스레드(ThreadPoolExecutor) 기반의 병렬 번역을 기본 제공합니다.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Callable
import concurrent.futures

# 진행률 콜백 타입: (비율 0.0~1.0, 메시지)
ProgressCallback = Callable[[float, str], None]

class BaseTranslator(ABC):
    """
    모든 번역 엔진이 상속받아야 하는 추상 기본 클래스입니다.
    """

    @abstractmethod
    def translate(self, text: str, src: str, dest: str) -> str:
        """
        단일 텍스트를 번역합니다.

        Args:
            text (str): 번역할 원본 텍스트
            src (str): 원본 언어 코드 (예: 'en')
            dest (str): 대상 언어 코드 (예: 'ko')

        Returns:
            str: 번역된 텍스트. 실패 시 원문을 반환하거나 빈 문자열을 반환할 수 있습니다.
        """
        pass

    def translate_batch(
        self,
        sentences: List[str],
        src: str,
        dest: str,
        max_workers: int = 1,
        progress_cb: Optional[ProgressCallback] = None
    ) -> List[str]:
        """
        여러 문장을 일괄 번역합니다. 기본적으로 ThreadPoolExecutor를 사용하여 병렬 처리합니다.

        Args:
            sentences (List[str]): 번역할 문장 리스트
            src (str): 원본 언어 코드
            dest (str): 대상 언어 코드
            max_workers (int): 병렬 처리에 사용할 스레드 수 (기본값: 1)
            progress_cb (Optional[ProgressCallback]): 진행률 콜백 함수

        Returns:
            List[str]: 번역된 문장 리스트 (입력 순서 유지)
        """
        total = len(sentences)
        if total == 0:
            return []

        if max_workers > 1:
            # 병렬 처리 (as_completed 사용으로 실시간 진행률 업데이트)
            results_map = {} # {index: translated_text}
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Future 객체와 원본 인덱스 매핑
                future_to_idx = {
                    executor.submit(self.translate, s, src, dest): i 
                    for i, s in enumerate(sentences)
                }
                
                completed_count = 0
                for future in concurrent.futures.as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    try:
                        translated_text = future.result()
                        results_map[idx] = translated_text if translated_text is not None else ""
                    except Exception as e:
                        results_map[idx] = "" # 에러 시 빈 문자열
                    
                    completed_count += 1
                    if progress_cb:
                        progress_cb(completed_count / total, f"번역 중... ({completed_count}/{total})")
            
            # 인덱스 순서대로 결과 리스트 재구성
            return [results_map[i] for i in range(total)]
        else:
            # 순차 처리
            results = []
            for idx, s in enumerate(sentences, start=1):
                translated = self.translate(s, src, dest)
                results.append(translated if translated is not None else "")
                if progress_cb:
                    progress_cb(idx / total, f"번역 중... ({idx}/{total})")
            return results

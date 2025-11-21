import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import logging
from datetime import datetime

@dataclass
class TimeRecord:
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration: float = 0.0

@dataclass
class StatRecord:
    name: str
    count: int = 0
    volume: float = 0.0  # 글자 수, 이미지 크기 등
    total_duration: float = 0.0
    unit: str = ""  # "chars", "words", "bytes" 등

class Benchmark:
    def __init__(self):
        self.records: List[TimeRecord] = []
        self.stats: Dict[str, StatRecord] = {}
        self.active_timers: Dict[str, float] = {}
        self._start_time = time.time()
        self.enabled = False  # 기본값은 False, main.py에서 활성화
        
        # 실행 메타데이터 (리포트에 표시용)
        self.max_workers = None  # main.py에서 설정
        self.sequential = None   # main.py에서 설정

    def start(self, name: str):
        """타이머 시작"""
        if not self.enabled:
            return
        if name in self.active_timers:
            pass
        self.active_timers[name] = time.time()

    def end(self, name: str):
        """타이머 종료 및 기록"""
        if not self.enabled:
            return
        if name not in self.active_timers:
            return
        
        start_time = self.active_timers.pop(name)
        end_time = time.time()
        duration = end_time - start_time
        
        self.records.append(TimeRecord(name, start_time, end_time, duration))

    def add_manual_record(self, name: str, start_time: float, end_time: float):
        """수동으로 시간 기록 추가 (예: Import Time)"""
        if not self.enabled:
            return
        duration = end_time - start_time
        self.records.append(TimeRecord(name, start_time, end_time, duration))

    def add_stat(self, name: str, duration: float, count: int = 1, volume: float = 0.0, unit: str = ""):
        """통계 데이터 추가 (예: 이미지 저장 1회, 0.5초 소요)"""
        if not self.enabled:
            return
        
        if name not in self.stats:
            self.stats[name] = StatRecord(name, unit=unit)
        
        record = self.stats[name]
        record.count += count
        record.volume += volume
        record.total_duration += duration
        record.unit = unit

    def report(self) -> str:
        """벤치마크 리포트 생성"""
        if not self.enabled:
            return ""

        total_duration = time.time() - self._start_time
        
        lines = []
        lines.append("=" * 60)
        lines.append(f"벤치마크 리포트 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        lines.append("=" * 60)
        
        # 실행 설정 정보 표시
        if self.max_workers is not None:
            mode = "순차(Sequential)" if self.sequential else f"병렬(Parallel)"
            lines.append(f"실행 모드: {mode}")
            lines.append(f"워커 수 (max-workers): {self.max_workers}")
            lines.append("-" * 60)
        
        lines.append(f"전체 실행 시간: {total_duration:.2f}초")
        lines.append("-" * 60)
        lines.append(f"{'작업명':<40} | {'소요 시간':<10}")
        lines.append("-" * 60)
        
        # 1. 일반 타이머 기록
        sorted_records = sorted(self.records, key=lambda r: r.start_time)
        for record in sorted_records:
            lines.append(f"{record.name:<40} | {record.duration:.2f}초")
            
        lines.append("-" * 60)
        
        # 2. 통계 기록 (있을 경우)
        if self.stats:
            lines.append(f"{'통계 항목':<30} | {'횟수':<6} | {'평균 시간':<10} | {'처리량 (Throughput)'}")
            lines.append("-" * 60)
            for name, stat in self.stats.items():
                avg_time = stat.total_duration / stat.count if stat.count > 0 else 0
                throughput = ""
                if stat.volume > 0 and stat.total_duration > 0:
                    tps = stat.volume / stat.total_duration
                    throughput = f"{tps:.1f} {stat.unit}/초"
                
                lines.append(f"{name:<30} | {stat.count:<6} | {avg_time:.4f}초    | {throughput}")
            lines.append("-" * 60)

        lines.append("=" * 60)
        return "\n".join(lines)

    def save_to_file(self, filepath: str):
        """리포트를 파일에 추가(append)"""
        if not self.enabled:
            return

        report_content = self.report()
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write("\n\n")
                f.write(report_content)
            logging.info(f"Benchmark report saved to {filepath}")
        except Exception as e:
            logging.error(f"Failed to save benchmark report: {e}")

# 전역 인스턴스
global_benchmark = Benchmark()

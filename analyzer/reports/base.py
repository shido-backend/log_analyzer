from abc import ABC, abstractmethod
from typing import Any, List
from concurrent.futures import ProcessPoolExecutor
import re

LOG_PATTERN = re.compile(
    r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s+(\w+)\s+([\w.]+):\s+(.*)$'
)
LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


class BaseReport(ABC):
    @abstractmethod
    def process_file(self, file_path: str) -> Any:
        pass

    @abstractmethod
    def merge_results(self, results: List[Any]) -> Any:
        pass

    @abstractmethod
    def format_report(self, merged_data: Any) -> str:
        pass

    def execute(self, files: List[str]) -> str:
        if not files:
            merged = self.merge_results([])
            return self.format_report(merged)
        with ProcessPoolExecutor(max_workers=min(4, len(files))) as executor:
            results = list(executor.map(self.process_file, files))
        merged = self.merge_results(results)
        return self.format_report(merged)

from collections import defaultdict
from typing import Dict, List, Optional
from analyzer.reports.base import BaseReport, LOG_PATTERN, LEVELS
import re


def default_dict_factory() -> defaultdict:
    return defaultdict(int)


class HandlersReport(BaseReport):
    def __init__(self):
        self.logger_name = 'django.requests'
        self.handler_pattern = re.compile(r'^(GET|POST|PUT|DELETE|PATCH)\s+(\S+)')

    def process_file(self, file_path: str) -> Dict[str, Dict[str, int]]:
        counts = defaultdict(default_dict_factory)
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                self._process_line(line, counts)
        return dict(counts)

    def _process_line(self, line: str, counts: Dict[str, Dict[str, int]]) -> None:
        log_entry = self._parse_log_line(line)
        if not log_entry:
            return
        if log_entry['logger'] == 'django.request':
            if handler := self._extract_handler(log_entry['message']):
                counts[handler][log_entry['level']] += 1

    def _parse_log_line(self, line: str) -> Optional[dict]:
        match = LOG_PATTERN.match(line.strip())
        if not match:
            return None
        _, level, logger, message = match.groups()
        return {'level': level.upper(), 'logger': logger, 'message': message}

    def _extract_handler(self, message: str) -> Optional[str]:
        if message.startswith(('GET ', 'POST ', 'PUT ', 'DELETE ', 'PATCH ')):
            parts = message.split()
            return parts[1] if len(parts) > 1 else None
        elif 'Internal Server Error:' in message:
            parts = message.split()
            for part in parts:
                if part.startswith('/'):
                    return part
        return None

    def merge_results(self, results: List[Dict[str, Dict[str, int]]]) -> Dict[str, Dict[str, int]]:
        merged: Dict[str, Dict[str, int]] = defaultdict(default_dict_factory)
        for result in results:
            for handler, levels in result.items():
                for level, count in levels.items():
                    merged[handler][level] += count
        return dict(merged)

    def format_report(self, merged_data: Dict[str, Dict[str, int]]) -> str:
        sorted_handlers = sorted(merged_data.keys())
        total: Dict[str, int] = defaultdict(int)
        rows = []

        for handler in sorted_handlers:
            row = [handler]
            for level in LEVELS:
                count = merged_data[handler].get(level, 0)
                row.append(str(count))
                total[level] += count
            rows.append(row)

        total_requests = sum(total.values())
        total_row = ['TOTAL'] + [str(total[level]) for level in LEVELS]

        headers = ['HANDLER'] + LEVELS
        all_rows = [headers] + rows + [total_row]
        col_widths = [
            max(len(str(row[i])) for row in all_rows)
            for i in range(len(headers))
        ]

        separator = '  '.join('-' * w for w in col_widths)
        formatted = [
            f"Total requests: {total_requests}\n",
            '  '.join(h.ljust(w) for h, w in zip(headers, col_widths)),
            separator
        ]
        formatted.extend(
            '  '.join(cell.ljust(w) for cell, w in zip(row, col_widths))
            for row in rows
        )
        formatted.extend([
            separator,
            '  '.join(cell.ljust(w) for cell, w in zip(total_row, col_widths))
        ])
        return '\n'.join(formatted)

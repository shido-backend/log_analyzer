import pytest
from analyzer.reports.base import BaseReport, LOG_PATTERN


class ConcreteReport(BaseReport):
    def process_file(self, file_path: str) -> dict:
        return {"test": 1}

    def merge_results(self, results: list) -> dict:
        return {"merged": sum(r["test"] for r in results)}

    def format_report(self, merged_data: dict) -> str:
        return str(merged_data)


class FaultyReport(BaseReport):
    def process_file(self, file_path: str) -> dict:
        raise ValueError("Processing error")

    def merge_results(self, results: list) -> dict:
        return {"merged": 0}

    def format_report(self, merged_data: dict) -> str:
        return str(merged_data)


def test_base_report_abstract_methods():
    with pytest.raises(TypeError):
        BaseReport()


def test_concrete_report_execute():
    report = ConcreteReport()
    result = report.execute(["file1", "file2"])
    assert result == "{'merged': 2}"


def test_concrete_report_execute_empty_files():
    report = ConcreteReport()
    result = report.execute([])
    assert result == "{'merged': 0}"


def test_concrete_report_execute_single_file():
    report = ConcreteReport()
    result = report.execute(["file1"])
    assert result == "{'merged': 1}"


def test_concrete_report_execute_multiple_files():
    report = ConcreteReport()
    result = report.execute(["file1", "file2", "file3", "file4", "file5"])
    assert result == "{'merged': 5}"


def test_concrete_report_process_file_exception():
    report = FaultyReport()
    with pytest.raises(ValueError, match="Processing error"):
        report.execute(["file1"])


def test_log_pattern():
    line = "2023-01-01 12:00:00,000 INFO django.request: GET /api/test/"
    match = LOG_PATTERN.match(line)
    assert match
    assert match.groups() == (
        "2023-01-01 12:00:00,000",
        "INFO",
        "django.request",
        "GET /api/test/"
    )


def test_log_pattern_invalid():
    line = "Invalid log line"
    match = LOG_PATTERN.match(line)
    assert match is None

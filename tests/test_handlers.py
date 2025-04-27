import pytest
from analyzer.reports.handlers import HandlersReport
from io import StringIO


@pytest.fixture
def handlers_report():
    return HandlersReport()


def test_process_file(handlers_report, monkeypatch):
    log_data = """2023-01-01 12:00:00,000 INFO django.request: GET /api/test/
2023-01-01 12:00:01,000 DEBUG django.request: POST /api/users/
2023-01-01 12:00:02,000 WARNING django.request: Internal Server Error: /api/error/"""

    def mock_open(*args, **kwargs):
        return StringIO(log_data)

    monkeypatch.setattr('builtins.open', mock_open)
    result = handlers_report.process_file('dummy.log')
    assert '/api/test/' in result
    assert result['/api/test/']['INFO'] == 1
    assert '/api/users/' in result
    assert result['/api/users/']['DEBUG'] == 1
    assert '/api/error/' in result
    assert result['/api/error/']['WARNING'] == 1


def test_process_file_invalid_lines(handlers_report, monkeypatch):
    log_data = """Invalid log line
Another invalid line"""

    def mock_open(*args, **kwargs):
        return StringIO(log_data)

    monkeypatch.setattr('builtins.open', mock_open)
    result = handlers_report.process_file('dummy.log')
    assert result == {}


def test_format_report(handlers_report):
    test_data = {
        '/api': {'DEBUG': 5, 'INFO': 3},
        '/test': {'WARNING': 2, 'ERROR': 1}
    }
    report = handlers_report.format_report(test_data)
    assert 'DEBUG' in report
    assert 'INFO' in report
    assert 'WARNING' in report
    assert 'ERROR' in report
    assert 'Total requests: 11' in report
    assert '/api' in report
    assert '/test' in report


def test_merge_results(handlers_report):
    data1 = {'/api': {'INFO': 2}}
    data2 = {'/api': {'INFO': 3}, '/test': {'DEBUG': 1}}
    data3 = {'/api': {'ERROR': 1}, '/test': {'DEBUG': 2}}
    merged = handlers_report.merge_results([data1, data2, data3])
    assert merged['/api']['INFO'] == 5
    assert merged['/api']['ERROR'] == 1
    assert merged['/test']['DEBUG'] == 3


def test_parse_log_line(handlers_report):
    line = "2023-01-01 12:00:00,000 INFO django.request: GET /api/test/"
    result = handlers_report._parse_log_line(line)
    assert result == {
        'level': 'INFO',
        'logger': 'django.request',
        'message': 'GET /api/test/'
    }

    invalid_line = "Invalid log line"
    assert handlers_report._parse_log_line(invalid_line) is None


def test_extract_handler(handlers_report):
    assert handlers_report._extract_handler("GET /api/test/") == "/api/test/"
    assert handlers_report._extract_handler("POST /api/users/") == "/api/users/"
    assert handlers_report._extract_handler("Internal Server Error: /api/error/") == "/api/error/"
    assert handlers_report._extract_handler("Some other message") is None

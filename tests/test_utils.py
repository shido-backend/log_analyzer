import pytest
from analyzer.utils import validate_files


def test_validate_files_existing(tmp_path):
    test_file = tmp_path / "test.log"
    test_file.write_text("test")
    validate_files([str(test_file)])


def test_validate_files_not_found():
    with pytest.raises(FileNotFoundError):
        validate_files(["nonexistent.log"])


def test_validate_files_not_a_file(tmp_path):
    dir_path = tmp_path / "directory"
    dir_path.mkdir()
    with pytest.raises(ValueError):
        validate_files([str(dir_path)])

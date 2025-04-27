from pathlib import Path
from typing import List


def validate_files(files: List[str]):
    for file in files:
        path = Path(file)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file}")

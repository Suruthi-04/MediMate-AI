import pytest
from pathlib import Path
from app.config import settings

def test_file_extension_validation():
    allowed = settings.ALLOWED_EXTENSIONS
    assert ".pdf" in allowed
    assert ".png" in allowed
    assert ".jpg" in allowed
    assert ".jpeg" in allowed

    disallowed_extensions = [".exe", ".bat", ".zip", ".docx", ".sh", ".py"]
    for ext in disallowed_extensions:
        assert ext not in allowed

def test_file_size_limits():
    assert settings.MAX_FILE_SIZE_MB == 15
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    assert max_bytes == 15728640

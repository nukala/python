import pytest
import os
import shutil
from etf_parser import get_cached_content, save_to_cache, CACHE_DIR, clear_cache

@pytest.fixture(autouse=True)
def setup_teardown():
    """Wipes cache before/after every test."""
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
    yield
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)

def test_offline_mode_ignores_expiry():
    content = "Ticker,Weight\nMU,5.0"
    save_to_cache("OFFLINE_TEST", content)
    # Even if expiry is -1 (expired), offline=True should return the data
    assert get_cached_content("OFFLINE_TEST", -1, offline=True) == content

def test_cache_cleanup_removes_dir():
    save_to_cache("TEMP", "data")
    assert os.path.exists(CACHE_DIR)
    clear_cache()
    assert not os.path.exists(CACHE_DIR)

def test_get_cached_content_returns_none_when_empty():
    assert get_cached_content("NONEXISTENT", 60) is None
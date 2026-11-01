import os
import pytest
from src.config import Settings

def test_settings_load_defaults(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key-12345")
    monkeypatch.setenv("DEBUG_MODE", "false")
    settings = Settings()
    assert settings.gemini_api_key == "test-api-key-12345"
    assert settings.debug_mode is False
    assert "flash" in settings.model_name

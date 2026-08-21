from __future__ import annotations

import pytest

from gartner_app.config import Settings


def test_settings_default_to_json_backend(monkeypatch) -> None:
    monkeypatch.delenv("DATA_BACKEND", raising=False)
    settings = Settings.from_env(dotenv=False)
    assert settings.data_backend == "json"
    assert settings.couchdb_url == "http://127.0.0.1:5984"


def test_settings_reject_unknown_backend(monkeypatch) -> None:
    monkeypatch.setenv("DATA_BACKEND", "filesystem-ish")
    with pytest.raises(ValueError, match="DATA_BACKEND"):
        Settings.from_env(dotenv=False)

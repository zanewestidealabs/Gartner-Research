from __future__ import annotations

from pathlib import Path

import pytest

from gartner_app.repositories.json_backend import LegacyJsonRepository


def test_read_and_atomic_write(tmp_path: Path) -> None:
    repository = LegacyJsonRepository(tmp_path)
    repository.write_atomic("example.json", {"value": 2})

    assert repository.read("example.json") == {"value": 2}
    assert not (tmp_path / ".example.json.tmp").exists()


@pytest.mark.parametrize(
    "path",
    ["../outside.json", "not-json.txt", "C:/Windows/system.json"],
)
def test_rejects_unsafe_paths(tmp_path: Path, path: str) -> None:
    repository = LegacyJsonRepository(tmp_path)
    with pytest.raises(ValueError):
        repository.resolve(path)

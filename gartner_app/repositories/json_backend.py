"""Safe compatibility repository for legacy JSON files."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class LegacyJsonRepository:
    """Read/write JSON under one repository root during migration."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def resolve(self, relative_path: str | Path) -> Path:
        candidate = (self.root / relative_path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("JSON path escapes the repository root") from exc
        if candidate.suffix.lower() != ".json":
            raise ValueError("legacy repository only accepts JSON paths")
        return candidate

    def read(self, relative_path: str | Path) -> Any:
        path = self.resolve(relative_path)
        with path.open("r", encoding="utf-8-sig") as source:
            return json.load(source)

    def write_atomic(self, relative_path: str | Path, value: Any) -> None:
        path = self.resolve(relative_path)
        temporary = path.with_name(f".{path.name}.tmp")
        try:
            with temporary.open("w", encoding="utf-8", newline="\n") as target:
                json.dump(value, target, indent=2, ensure_ascii=False)
                target.write("\n")
                target.flush()
                os.fsync(target.fileno())
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()

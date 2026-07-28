from __future__ import annotations

from pathlib import Path


class SkillLibrary:
    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]

    def load(self, relative_path: str) -> str:
        path = self.repo_root / relative_path
        if not path.exists():
            raise FileNotFoundError(f"Skill not found: {relative_path}")
        return path.read_text(encoding="utf-8")

    def combine(self, *paths: str) -> str:
        return "\n\n---\n\n".join(self.load(path) for path in paths)
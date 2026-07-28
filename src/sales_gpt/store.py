from __future__ import annotations

import json
import os
import re
from pathlib import Path

from .models import Account, SalesContext


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


class ContextStore:
    def __init__(self, root: str | None = None) -> None:
        self.root = Path(root or os.getenv("SALES_GPT_DATA_DIR", ".sales-gpt"))
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, account_name: str) -> Path:
        return self.root / f"{_slug(account_name)}.json"

    def load(self, account_name: str) -> SalesContext:
        path = self.path_for(account_name)
        if not path.exists():
            return SalesContext(account=Account(name=account_name))
        return SalesContext.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, context: SalesContext) -> Path:
        path = self.path_for(context.account.name)
        path.write_text(json.dumps(context.model_dump(mode="json"), indent=2), encoding="utf-8")
        return path

    def list_contexts(self) -> list[SalesContext]:
        contexts: list[SalesContext] = []
        for path in sorted(self.root.glob("*.json")):
            try:
                contexts.append(SalesContext.model_validate_json(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return contexts

    def delete(self, account_name: str) -> bool:
        path = self.path_for(account_name)
        if not path.exists():
            return False
        path.unlink()
        return True
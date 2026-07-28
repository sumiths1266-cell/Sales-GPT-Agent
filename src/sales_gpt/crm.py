from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .models import Account, Opportunity, SalesContext, Stakeholder


class CRMConnector(Protocol):
    def pull_accounts(self) -> list[SalesContext]: ...
    def push_context(self, context: SalesContext) -> None: ...


@dataclass
class CSVCRMImporter:
    path: Path

    def pull_accounts(self) -> list[SalesContext]:
        contexts: list[SalesContext] = []
        with self.path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                name = (row.get("account") or row.get("account_name") or row.get("company") or "").strip()
                if not name:
                    continue
                amount = _float(row.get("amount"))
                stakeholder_name = (row.get("contact") or row.get("contact_name") or "").strip()
                stakeholders = []
                if stakeholder_name:
                    stakeholders.append(Stakeholder(
                        name=stakeholder_name,
                        title=(row.get("title") or "").strip() or None,
                        role=(row.get("role") or "").strip() or None,
                    ))
                contexts.append(SalesContext(
                    account=Account(
                        name=name,
                        website=(row.get("website") or "").strip() or None,
                        industry=(row.get("industry") or "").strip() or None,
                    ),
                    stakeholders=stakeholders,
                    opportunity=Opportunity(
                        stage=(row.get("stage") or "target").strip(),
                        amount=amount,
                    ),
                ))
        return contexts

    def push_context(self, context: SalesContext) -> None:
        raise NotImplementedError("CSV connector is import-only")


def _float(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(value.replace(",", "").replace("$", ""))
    except ValueError:
        return None
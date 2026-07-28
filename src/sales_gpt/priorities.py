from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from .health import score_deal
from .models import SalesContext


@dataclass
class Priority:
    account: str
    score: int
    category: str
    reason: str
    action: str


def _days_since_last_activity(context: SalesContext) -> int | None:
    dated = [i.date for i in context.interactions if i.date]
    if not dated:
        return None
    return (date.today() - max(dated)).days


def prioritize(context: SalesContext) -> Priority:
    health = score_deal(context)
    score = 0
    reasons: list[str] = []
    days = _days_since_last_activity(context)

    if context.opportunity.amount:
        score += min(int(context.opportunity.amount / 10000), 25)
    if health.label == "At Risk":
        score += 25
        reasons.append("deal is at risk")
    elif health.label == "Watch":
        score += 15
        reasons.append("deal needs attention")

    if days is None:
        score += 10
        reasons.append("no dated activity recorded")
    elif days >= 14:
        score += 25
        reasons.append(f"stalled for {days} days")
    elif days >= 7:
        score += 15
        reasons.append(f"no activity for {days} days")

    if context.opportunity.risks:
        score += min(len(context.opportunity.risks) * 4, 20)
    if context.account.icp_score is not None and context.account.icp_score >= 75 and context.opportunity.stage == "target":
        score += 20
        reasons.append("high-fit prospect")

    action = context.opportunity.next_actions[0] if context.opportunity.next_actions else "Run an AI deal review and establish the next buyer commitment."
    category = "Prospect" if context.opportunity.stage == "target" else "Deal"
    return Priority(context.account.name, min(score, 100), category, ", ".join(reasons) or "active account", action)


def daily_priorities(contexts: list[SalesContext], limit: int = 10) -> list[Priority]:
    return sorted((prioritize(c) for c in contexts), key=lambda p: p.score, reverse=True)[:limit]
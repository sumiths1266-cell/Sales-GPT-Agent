from __future__ import annotations

from dataclasses import dataclass

from .models import EvidenceStatus, SalesContext


@dataclass
class DealHealth:
    score: int
    label: str
    reasons: list[str]


def score_deal(context: SalesContext) -> DealHealth:
    score = 50
    reasons: list[str] = []
    fields = context.meddpicc.model_dump()
    confirmed = sum(1 for value in fields.values() if value["status"] == EvidenceStatus.confirmed.value)
    partial = sum(1 for value in fields.values() if value["status"] == EvidenceStatus.partial.value)
    score += confirmed * 5 + partial * 2

    if context.stakeholders:
        score += min(len(context.stakeholders) * 2, 8)
    else:
        score -= 8
        reasons.append("No stakeholders mapped")

    if context.opportunity.next_actions:
        score += 4
    else:
        score -= 5
        reasons.append("No defined next action")

    if context.opportunity.risks:
        penalty = min(len(context.opportunity.risks) * 3, 18)
        score -= penalty
        reasons.append(f"{len(context.opportunity.risks)} active risk(s)")

    if fields["identified_pain"]["status"] not in {"partial", "confirmed"}:
        score -= 10
        reasons.append("Pain is not buyer-validated")
    if fields["champion"]["status"] not in {"partial", "confirmed"}:
        score -= 8
        reasons.append("Champion is weak or unknown")
    if fields["economic_buyer"]["status"] not in {"partial", "confirmed"}:
        score -= 8
        reasons.append("Economic buyer is weak or unknown")

    score = max(0, min(100, score))
    label = "Healthy" if score >= 75 else "Watch" if score >= 50 else "At Risk"
    return DealHealth(score=score, label=label, reasons=reasons[:4])
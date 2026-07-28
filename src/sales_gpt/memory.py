from __future__ import annotations

from .models import SalesContext
from .results import WorkflowResult


def _merge_unique(existing: list[str], incoming: list[str]) -> list[str]:
    return list(dict.fromkeys([*existing, *incoming]))


def apply_result(context: SalesContext, result: WorkflowResult) -> SalesContext:
    if result.account_update:
        update = result.account_update
        if update.industry:
            context.account.industry = update.industry
        if update.website:
            context.account.website = update.website
        if update.icp_score is not None:
            context.account.icp_score = update.icp_score
        context.account.signals = _merge_unique(context.account.signals, update.signals)

    if result.opportunity_update:
        update = result.opportunity_update
        if update.stage:
            context.opportunity.stage = update.stage
        context.opportunity.buyer_outcomes = _merge_unique(context.opportunity.buyer_outcomes, update.buyer_outcomes)
        context.opportunity.risks = _merge_unique(context.opportunity.risks, update.risks)
        context.opportunity.next_actions = update.next_actions or context.opportunity.next_actions

    if result.stakeholders:
        by_name = {stakeholder.name.lower(): stakeholder for stakeholder in context.stakeholders}
        for stakeholder in result.stakeholders:
            by_name[stakeholder.name.lower()] = stakeholder
        context.stakeholders = list(by_name.values())

    if result.meddpicc:
        context.meddpicc = result.meddpicc

    context.unknowns = _merge_unique(context.unknowns, result.unknowns)
    if result.next_actions:
        context.opportunity.next_actions = result.next_actions

    return context
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .models import MEDDPICC, Stakeholder


class AccountUpdate(BaseModel):
    industry: str | None = None
    website: str | None = None
    icp_score: float | None = None
    signals: list[str] = Field(default_factory=list)


class OpportunityUpdate(BaseModel):
    stage: str | None = None
    buyer_outcomes: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class WorkflowResult(BaseModel):
    summary: str
    facts: list[str] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    account_update: AccountUpdate | None = None
    opportunity_update: OpportunityUpdate | None = None
    stakeholders: list[Stakeholder] = Field(default_factory=list)
    meddpicc: MEDDPICC | None = None
    next_actions: list[str] = Field(default_factory=list)
    forecast_category: Literal["pipeline", "best_case", "commit", "closed_won", "closed_lost"] | None = None
    confidence: Literal["low", "medium", "high"] = "medium"
    seller_response: str
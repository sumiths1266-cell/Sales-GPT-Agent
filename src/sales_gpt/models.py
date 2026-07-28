from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EvidenceStatus(str, Enum):
    unknown = "unknown"
    hypothesis = "hypothesis"
    partial = "partial"
    confirmed = "confirmed"


class EvidenceField(BaseModel):
    status: EvidenceStatus = EvidenceStatus.unknown
    value: Any | None = None
    evidence: list[str] = Field(default_factory=list)
    next_question: str | None = None


class Stakeholder(BaseModel):
    name: str
    title: str | None = None
    role: str | None = None
    influence: str | None = None
    stance: str | None = None
    priorities: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class MEDDPICC(BaseModel):
    metrics: EvidenceField = Field(default_factory=EvidenceField)
    economic_buyer: EvidenceField = Field(default_factory=EvidenceField)
    decision_criteria: EvidenceField = Field(default_factory=EvidenceField)
    decision_process: EvidenceField = Field(default_factory=EvidenceField)
    paper_process: EvidenceField = Field(default_factory=EvidenceField)
    identified_pain: EvidenceField = Field(default_factory=EvidenceField)
    champion: EvidenceField = Field(default_factory=EvidenceField)
    competition: EvidenceField = Field(default_factory=EvidenceField)


class Interaction(BaseModel):
    date: date | None = None
    type: str
    summary: str
    commitments: list[str] = Field(default_factory=list)


class Account(BaseModel):
    name: str
    website: str | None = None
    industry: str | None = None
    icp_score: float | None = None
    signals: list[str] = Field(default_factory=list)


class Opportunity(BaseModel):
    stage: str = "target"
    amount: float | None = None
    target_close_date: date | None = None
    buyer_outcomes: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class SalesContext(BaseModel):
    account: Account
    stakeholders: list[Stakeholder] = Field(default_factory=list)
    opportunity: Opportunity = Field(default_factory=Opportunity)
    meddpicc: MEDDPICC = Field(default_factory=MEDDPICC)
    interactions: list[Interaction] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
from __future__ import annotations

import json

from .llm import SalesLLM
from .models import SalesContext
from .results import WorkflowResult
from .skills import SkillLibrary


PI = "skills/pi/pi-selling.md"
INDUSTRY = "skills/pi/industry-playbook.md"
DOSSIER = "skills/sdr/full-account-dossier.md"
WORKFLOWS = {
    "research": [PI, INDUSTRY, DOSSIER, "agents/sdr.md", "skills/sdr/account-research.md", "skills/sdr/icp-scoring.md", "skills/sdr/trigger-detection.md", "skills/sdr/outreach.md", "skills/ae/discovery.md", "skills/shared/next-best-action.md"],
    "prospect": [PI, INDUSTRY, DOSSIER, "agents/sdr.md", "skills/sdr/account-research.md", "skills/sdr/trigger-detection.md", "skills/sdr/outreach.md", "skills/shared/next-best-action.md"],
    "meeting-prep": [PI, INDUSTRY, "agents/sdr.md", "skills/sdr/meeting-prep.md", "skills/ae/discovery.md"],
    "transcript": [PI, INDUSTRY, "agents/account-executive.md", "skills/shared/transcript-analysis.md", "skills/ae/meddpicc.md", "skills/ae/stakeholder-mapping.md"],
    "follow-up": [PI, "agents/account-executive.md", "skills/shared/follow-up.md", "skills/shared/next-best-action.md"],
    "deal-review": [PI, INDUSTRY, "agents/sales-manager.md", "skills/ae/meddpicc.md", "skills/ae/deal-risk.md", "skills/ae/forecasting.md", "skills/shared/next-best-action.md"],
    "competitive": [PI, INDUSTRY, "skills/pi/competitive-battlecard.md", "skills/ae/competitive-strategy.md", "skills/shared/next-best-action.md"],
    "industry": [PI, INDUSTRY, DOSSIER, "agents/sdr.md", "skills/sdr/account-research.md", "skills/ae/discovery.md", "skills/sdr/outreach.md", "skills/shared/next-best-action.md"],
}


class SalesOrchestrator:
    def __init__(self, llm: SalesLLM | None = None, skills: SkillLibrary | None = None) -> None:
        self.llm = llm or SalesLLM()
        self.skills = skills or SkillLibrary()

    def run(self, workflow: str, context: SalesContext, request: str) -> WorkflowResult:
        if workflow not in WORKFLOWS:
            raise ValueError(f"Unknown workflow: {workflow}")
        playbook = self.skills.combine(*WORKFLOWS[workflow])
        instructions = (
            "You are Sales GPT Agent, supporting an enterprise seller of Pi by Paytm. Follow the supplied sales playbook. "
            "Never invent evidence or Pi claims. Clearly distinguish confirmed facts, public facts, seller-provided facts, hypotheses, and unknowns. "
            "Return structured updates only when supported by evidence. Preserve existing context unless new evidence improves it. "
            "For research/prospect/industry workflows, default to an outreach-ready dossier: account intelligence, Pi plays, actual named prospects where verifiable, prospect research, verified public LinkedIn links when available, personalized messaging, multithreading, discovery, sequence and next actions. "
            "Never fabricate people, profile URLs, contact details or installed technology. If a prospect/profile cannot be verified, state that and provide a search string. "
            "Sell business outcomes before product capabilities. The seller_response must be useful and actionable and end with prioritized next actions.\n\n" + playbook
        )
        payload = {"workflow": workflow, "sales_context": context.model_dump(mode="json"), "seller_request": request}
        return self.llm.run_structured(
            instructions=instructions,
            user_input=json.dumps(payload, indent=2),
            schema=WorkflowResult,
            web_search=workflow in {"research", "prospect", "competitive", "industry"},
        )
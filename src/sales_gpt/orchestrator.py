from __future__ import annotations

import json

from .llm import SalesLLM
from .models import SalesContext
from .results import WorkflowResult
from .skills import SkillLibrary


WORKFLOWS = {
    "research": ["agents/sdr.md", "skills/sdr/account-research.md", "skills/sdr/icp-scoring.md", "skills/sdr/trigger-detection.md"],
    "meeting-prep": ["agents/sdr.md", "skills/sdr/meeting-prep.md", "skills/ae/discovery.md"],
    "transcript": ["agents/account-executive.md", "skills/shared/transcript-analysis.md", "skills/ae/meddpicc.md", "skills/ae/stakeholder-mapping.md"],
    "deal-review": ["agents/sales-manager.md", "skills/ae/meddpicc.md", "skills/ae/deal-risk.md", "skills/ae/forecasting.md", "skills/shared/next-best-action.md"],
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
            "You are Sales GPT Agent. Follow the supplied sales playbook. "
            "Never invent evidence. Clearly distinguish confirmed facts, hypotheses, and unknowns. "
            "Return structured updates only when supported by evidence. Preserve existing context unless new evidence improves it. "
            "The seller_response must be a concise, useful answer for the seller and end with prioritized next actions.\n\n" + playbook
        )
        payload = {
            "workflow": workflow,
            "sales_context": context.model_dump(mode="json"),
            "seller_request": request,
        }
        return self.llm.run_structured(
            instructions=instructions,
            user_input=json.dumps(payload, indent=2),
            schema=WorkflowResult,
            web_search=workflow == "research",
        )
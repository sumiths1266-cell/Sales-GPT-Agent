from sales_gpt.models import Account, SalesContext
from sales_gpt.orchestrator import SalesOrchestrator
from sales_gpt.results import WorkflowResult


class FakeLLM:
    def __init__(self):
        self.calls = []

    def run_structured(self, **kwargs):
        self.calls.append(kwargs)
        return WorkflowResult(
            summary="No evidence supplied",
            facts=[],
            hypotheses=[],
            unknowns=["Buyer pain is unknown"],
            next_actions=["Ask discovery questions"],
            seller_response="Buyer pain is unknown. Ask discovery questions.",
        )


class FakeSkills:
    def combine(self, *paths):
        return "PLAYBOOK:" + ",".join(paths)


def test_research_enables_web_search():
    llm = FakeLLM()
    orchestrator = SalesOrchestrator(llm=llm, skills=FakeSkills())
    orchestrator.run("research", SalesContext(account=Account(name="Acme")), "Research Acme")
    assert llm.calls[0]["web_search"] is True


def test_competitive_enables_web_search():
    llm = FakeLLM()
    orchestrator = SalesOrchestrator(llm=llm, skills=FakeSkills())
    orchestrator.run("competitive", SalesContext(account=Account(name="Acme")), "Compare Pi with Yellow.ai")
    assert llm.calls[0]["web_search"] is True


def test_deal_review_does_not_enable_web_search():
    llm = FakeLLM()
    orchestrator = SalesOrchestrator(llm=llm, skills=FakeSkills())
    result = orchestrator.run("deal-review", SalesContext(account=Account(name="Acme")), "Review deal")
    assert llm.calls[0]["web_search"] is False
    assert result.facts == []
    assert "Buyer pain is unknown" in result.unknowns


def test_unknown_workflow_is_rejected():
    orchestrator = SalesOrchestrator(llm=FakeLLM(), skills=FakeSkills())
    try:
        orchestrator.run("made-up", SalesContext(account=Account(name="Acme")), "test")
    except ValueError as exc:
        assert "Unknown workflow" in str(exc)
    else:
        raise AssertionError("Expected unknown workflow to raise ValueError")
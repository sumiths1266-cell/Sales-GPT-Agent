from sales_gpt.health import score_deal
from sales_gpt.models import Account, EvidenceField, EvidenceStatus, SalesContext, Stakeholder


def test_empty_deal_is_at_risk():
    context = SalesContext(account=Account(name="Acme"))
    health = score_deal(context)
    assert health.label == "At Risk"
    assert health.score < 50


def test_confirmed_meddpicc_and_stakeholders_improve_health():
    context = SalesContext(account=Account(name="Acme"))
    confirmed = EvidenceField(status=EvidenceStatus.confirmed, value="confirmed", evidence=["buyer evidence"])
    context.meddpicc.metrics = confirmed.model_copy(deep=True)
    context.meddpicc.identified_pain = confirmed.model_copy(deep=True)
    context.meddpicc.champion = confirmed.model_copy(deep=True)
    context.meddpicc.economic_buyer = confirmed.model_copy(deep=True)
    context.stakeholders = [Stakeholder(name="Jane", role="champion"), Stakeholder(name="Alex", role="economic buyer")]
    context.opportunity.next_actions = ["Schedule executive validation"]

    health = score_deal(context)
    assert health.score >= 75
    assert health.label == "Healthy"


def test_risks_reduce_health_score():
    context = SalesContext(account=Account(name="Acme"))
    baseline = score_deal(context).score
    context.opportunity.risks = ["No budget", "Security blocker", "No decision process"]
    assert score_deal(context).score < baseline
from datetime import date, timedelta

from sales_gpt.models import Account, Interaction, SalesContext
from sales_gpt.priorities import daily_priorities, prioritize


def test_high_fit_target_gets_prospect_priority():
    context = SalesContext(account=Account(name="Acme", icp_score=90))
    priority = prioritize(context)
    assert priority.category == "Prospect"
    assert "high-fit prospect" in priority.reason


def test_stalled_deal_is_prioritized():
    context = SalesContext(account=Account(name="Acme"))
    context.opportunity.stage = "discovery"
    context.interactions = [Interaction(date=date.today() - timedelta(days=20), type="meeting", summary="Discovery")]
    priority = prioritize(context)
    assert "stalled for" in priority.reason
    assert priority.score > 0


def test_daily_priorities_orders_highest_score_first():
    low = SalesContext(account=Account(name="Low"))
    low.opportunity.stage = "discovery"
    low.interactions = [Interaction(date=date.today(), type="call", summary="Current")]

    high = SalesContext(account=Account(name="High", icp_score=95))
    high.opportunity.amount = 200000
    high.opportunity.risks = ["Economic buyer unknown"]

    priorities = daily_priorities([low, high])
    assert priorities[0].account == "High"
    assert priorities[0].score >= priorities[1].score
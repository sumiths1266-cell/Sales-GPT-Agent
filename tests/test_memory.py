from sales_gpt.memory import apply_result
from sales_gpt.models import Account, EvidenceField, EvidenceStatus, MEDDPICC, SalesContext, Stakeholder
from sales_gpt.results import AccountUpdate, OpportunityUpdate, WorkflowResult


def test_apply_result_updates_context():
    context = SalesContext(account=Account(name="Acme"))
    meddpicc = MEDDPICC(
        identified_pain=EvidenceField(
            status=EvidenceStatus.confirmed,
            value="Manual workflow is slow",
            evidence=["Buyer stated the process takes two days"],
        )
    )
    result = WorkflowResult(
        summary="Discovery analyzed",
        facts=["Buyer has a manual workflow"],
        account_update=AccountUpdate(industry="Software", signals=["Hiring growth"]),
        opportunity_update=OpportunityUpdate(stage="discovery", risks=["No economic buyer access"]),
        stakeholders=[Stakeholder(name="Jane Doe", title="VP Operations", role="business owner")],
        meddpicc=meddpicc,
        next_actions=["Ask Jane to introduce the economic buyer"],
        seller_response="The deal has a confirmed pain but lacks economic buyer access.",
    )

    updated = apply_result(context, result)

    assert updated.account.industry == "Software"
    assert updated.opportunity.stage == "discovery"
    assert updated.stakeholders[0].name == "Jane Doe"
    assert updated.meddpicc.identified_pain.status == EvidenceStatus.confirmed
    assert updated.opportunity.next_actions == ["Ask Jane to introduce the economic buyer"]
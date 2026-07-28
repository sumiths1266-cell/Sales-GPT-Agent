from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from .crm import CSVCRMImporter
from .health import score_deal
from .memory import apply_result
from .models import Interaction
from .orchestrator import SalesOrchestrator
from .store import ContextStore

st.set_page_config(page_title="Sales GPT Agent", page_icon="💼", layout="wide")
store = ContextStore()
orchestrator = SalesOrchestrator()


def run_workflow(account: str, workflow: str, request: str):
    context = store.load(account)
    with st.spinner("Sales GPT is working..."):
        result = orchestrator.run(workflow, context, request)
    context = apply_result(context, result)
    store.save(context)
    return result, context


def meddpicc_rows(context):
    return [{"Dimension": n.replace("_", " ").title(), "Status": f["status"], "Value": str(f.get("value") or ""), "Next question": f.get("next_question") or ""} for n, f in context.meddpicc.model_dump().items()]


def pipeline_rows():
    rows = []
    for context in store.list_contexts():
        health = score_deal(context)
        rows.append({
            "Account": context.account.name,
            "Stage": context.opportunity.stage,
            "Amount": context.opportunity.amount,
            "ICP": context.account.icp_score,
            "Health": health.score,
            "Health label": health.label,
            "Stakeholders": len(context.stakeholders),
            "Risks": len(context.opportunity.risks),
            "Next action": context.opportunity.next_actions[0] if context.opportunity.next_actions else "",
        })
    return rows


st.title("Sales GPT Agent")
st.caption("AI-native SDR + Account Executive workspace")

page = st.sidebar.radio("Workspace", ["Pipeline", "Account"])

if page == "Pipeline":
    st.subheader("Pipeline command center")
    contexts = store.list_contexts()
    total_pipeline = sum(c.opportunity.amount or 0 for c in contexts)
    at_risk = sum(1 for c in contexts if score_deal(c).label == "At Risk")
    c1, c2, c3 = st.columns(3)
    c1.metric("Accounts", len(contexts))
    c2.metric("Pipeline", f"${total_pipeline:,.0f}")
    c3.metric("At-risk deals", at_risk)
    rows = pipeline_rows()
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No accounts yet. Import a CRM CSV or open an account workspace.")

    st.markdown("### CRM import")
    crm_file = st.file_uploader("Import accounts/opportunities from CSV", type=["csv"])
    st.caption("Supported columns include account/account_name/company, website, industry, stage, amount, contact/contact_name, title, and role.")
    if crm_file and st.button("Import CRM data"):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(crm_file.getvalue())
            tmp_path = Path(tmp.name)
        imported = CSVCRMImporter(tmp_path).pull_accounts()
        for imported_context in imported:
            existing = store.load(imported_context.account.name)
            existing.account.website = imported_context.account.website or existing.account.website
            existing.account.industry = imported_context.account.industry or existing.account.industry
            existing.opportunity.stage = imported_context.opportunity.stage or existing.opportunity.stage
            existing.opportunity.amount = imported_context.opportunity.amount or existing.opportunity.amount
            if imported_context.stakeholders:
                existing.stakeholders.extend(imported_context.stakeholders)
            store.save(existing)
        tmp_path.unlink(missing_ok=True)
        st.success(f"Imported {len(imported)} account/opportunity row(s). Refresh to view the pipeline.")
    st.stop()

account = st.sidebar.text_input("Account", placeholder="e.g. Acme Corp")
if not account:
    st.info("Enter an account name to open its sales workspace.")
    st.stop()

context = store.load(account)
health = score_deal(context)
st.sidebar.markdown(f"**Stage:** {context.opportunity.stage}")
st.sidebar.markdown(f"**Deal health:** {health.score}/100 — {health.label}")
st.sidebar.markdown(f"**ICP:** {context.account.icp_score if context.account.icp_score is not None else 'Not scored'}")

research_tab, workspace_tab, transcript_tab, activity_tab, copilot_tab = st.tabs(["Research", "Deal Workspace", "Transcript", "Activity", "Copilot"])

with research_tab:
    st.subheader("Account research")
    research_request = st.text_area("Research objective", value="Research this account, assess ICP fit, identify recent triggers, likely personas, sales hypotheses, and recommend the next action.", height=120)
    if st.button("Research account", type="primary"):
        result, context = run_workflow(account, "research", research_request)
        st.markdown(result.seller_response)
        st.success("Account memory updated.")
    if context.account.signals:
        st.markdown("### Signals")
        for signal in context.account.signals:
            st.markdown(f"- {signal}")

with workspace_tab:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stage", context.opportunity.stage)
    c2.metric("Deal health", f"{health.score}/100", health.label)
    c3.metric("ICP", context.account.icp_score if context.account.icp_score is not None else "—")
    c4.metric("Stakeholders", len(context.stakeholders))
    if health.reasons:
        st.caption("Health drivers: " + " • ".join(health.reasons))

    st.markdown("### MEDDPICC")
    st.dataframe(meddpicc_rows(context), use_container_width=True, hide_index=True)
    left, right = st.columns(2)
    with left:
        st.markdown("### Stakeholders")
        if context.stakeholders:
            st.dataframe([s.model_dump() for s in context.stakeholders], use_container_width=True, hide_index=True)
        else:
            st.caption("No stakeholders mapped yet.")
    with right:
        st.markdown("### Next actions")
        for action in context.opportunity.next_actions:
            st.markdown(f"- {action}")
        st.markdown("### Risks")
        for risk in context.opportunity.risks:
            st.markdown(f"- {risk}")
    if st.button("Run deal review"):
        result, context = run_workflow(account, "deal-review", "Review the opportunity. Assess MEDDPICC, stakeholder coverage, deal risks, forecast quality, and recommend the three highest-leverage next actions.")
        st.markdown(result.seller_response)

with transcript_tab:
    st.subheader("Analyze a sales call")
    uploaded = st.file_uploader("Upload transcript", type=["txt", "md"])
    pasted = st.text_area("Or paste transcript", height=260)
    if st.button("Analyze transcript", type="primary"):
        transcript = uploaded.getvalue().decode("utf-8") if uploaded is not None else pasted
        if not transcript.strip():
            st.warning("Add a transcript first.")
        else:
            result, context = run_workflow(account, "transcript", f"Analyze this sales-call transcript and update the opportunity evidence:\n\n{transcript}")
            st.markdown(result.seller_response)
            st.success("Deal memory updated when supported by evidence.")

with activity_tab:
    st.subheader("Activity timeline")
    activity_type = st.selectbox("Activity type", ["call", "email", "meeting", "note", "task"])
    summary = st.text_area("Summary / task")
    commitments = st.text_input("Commitments or due action", placeholder="Optional")
    if st.button("Add activity") and summary.strip():
        context.interactions.append(Interaction(type=activity_type, summary=summary.strip(), commitments=[commitments.strip()] if commitments.strip() else []))
        store.save(context)
        st.success("Activity saved.")
    if context.interactions:
        for item in reversed(context.interactions):
            st.markdown(f"**{item.type.title()}** — {item.summary}")
            if item.commitments:
                st.caption("Commitment: " + "; ".join(item.commitments))

with copilot_tab:
    st.subheader("Sales copilot")
    prompt = st.text_area("Ask about this account or deal", placeholder="What are the biggest gaps in this deal and what should I do before my next meeting?", height=140)
    mode = st.selectbox("Mode", ["Deal review", "Meeting prep"])
    if st.button("Ask Sales GPT") and prompt.strip():
        workflow = "deal-review" if mode == "Deal review" else "meeting-prep"
        result, context = run_workflow(account, workflow, prompt)
        st.markdown(result.seller_response)
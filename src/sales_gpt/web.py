from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from .crm import CSVCRMImporter
from .health import score_deal
from .memory import apply_result
from .models import Interaction
from .orchestrator import SalesOrchestrator
from .priorities import daily_priorities
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


def pipeline_rows(contexts):
    rows = []
    for context in contexts:
        health = score_deal(context)
        rows.append({"Account": context.account.name, "Stage": context.opportunity.stage, "Amount": context.opportunity.amount, "ICP": context.account.icp_score, "Health": health.score, "Health label": health.label, "Stakeholders": len(context.stakeholders), "Risks": len(context.opportunity.risks), "Next action": context.opportunity.next_actions[0] if context.opportunity.next_actions else ""})
    return rows


st.title("Sales GPT Agent")
st.caption("AI-native SDR + Account Executive workspace")
page = st.sidebar.radio("Workspace", ["Today", "Pipeline", "Account"])

if page == "Today":
    contexts = store.list_contexts()
    st.subheader("Today's sales priorities")
    st.caption("Ranked from account fit, pipeline value, deal health, risks, inactivity, and known next actions.")
    priorities = daily_priorities(contexts)
    if not priorities:
        st.info("Add or import accounts to generate a daily priority list.")
    for index, priority in enumerate(priorities, start=1):
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"### {index}. {priority.account}")
            c1.write(f"**{priority.category}** · {priority.reason}")
            c1.write(f"**Do next:** {priority.action}")
            c2.metric("Priority", priority.score)
    st.stop()

if page == "Pipeline":
    st.subheader("Pipeline command center")
    contexts = store.list_contexts()
    total_pipeline = sum(c.opportunity.amount or 0 for c in contexts)
    at_risk = sum(1 for c in contexts if score_deal(c).label == "At Risk")
    c1, c2, c3 = st.columns(3)
    c1.metric("Accounts", len(contexts))
    c2.metric("Pipeline", f"${total_pipeline:,.0f}")
    c3.metric("At-risk deals", at_risk)
    rows = pipeline_rows(contexts)
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No accounts yet. Import a CRM CSV or open an account workspace.")
    st.markdown("### CRM import")
    crm_file = st.file_uploader("Import accounts/opportunities from CSV", type=["csv"])
    st.caption("Supported columns: account/account_name/company, website, industry, stage, amount, contact/contact_name, title, role.")
    if crm_file and st.button("Import CRM data"):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(crm_file.getvalue())
            tmp_path = Path(tmp.name)
        imported = CSVCRMImporter(tmp_path).pull_accounts()
        for item in imported:
            existing = store.load(item.account.name)
            existing.account.website = item.account.website or existing.account.website
            existing.account.industry = item.account.industry or existing.account.industry
            existing.opportunity.stage = item.opportunity.stage or existing.opportunity.stage
            existing.opportunity.amount = item.opportunity.amount or existing.opportunity.amount
            existing.stakeholders.extend(item.stakeholders)
            store.save(existing)
        tmp_path.unlink(missing_ok=True)
        st.success(f"Imported {len(imported)} row(s).")
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
    st.subheader("Account research & prospecting")
    research_request = st.text_area("Objective", value="Research this account, assess ICP fit, identify recent triggers, likely personas, sales hypotheses, and recommend who to contact and why.", height=120)
    c1, c2 = st.columns(2)
    if c1.button("Research account", type="primary"):
        result, context = run_workflow(account, "research", research_request)
        st.markdown(result.seller_response)
    if c2.button("Build prospecting plan"):
        result, context = run_workflow(account, "prospect", research_request + " Build an evidence-backed outreach angle and recommended entry persona.")
        st.markdown(result.seller_response)
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
    with right:
        st.markdown("### Next actions")
        for action in context.opportunity.next_actions:
            st.markdown(f"- {action}")
        st.markdown("### Risks")
        for risk in context.opportunity.risks:
            st.markdown(f"- {risk}")
    if st.button("Run deal review"):
        result, context = run_workflow(account, "deal-review", "Review the opportunity, challenge assumptions, assess MEDDPICC, stakeholder coverage, risks and forecast, then recommend the three highest-leverage next actions.")
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
    st.subheader("Activity & follow-up")
    activity_type = st.selectbox("Activity type", ["call", "email", "meeting", "note", "task"])
    summary = st.text_area("Summary / task")
    commitments = st.text_input("Commitments or due action", placeholder="Optional")
    if st.button("Add activity") and summary.strip():
        context.interactions.append(Interaction(type=activity_type, summary=summary.strip(), commitments=[commitments.strip()] if commitments.strip() else []))
        store.save(context)
        st.success("Activity saved.")
    if st.button("Draft follow-up"):
        result, context = run_workflow(account, "follow-up", "Draft a concise follow-up email from the latest interactions and deal context. Use only supported buyer facts and commitments. Include a subject suggestion and clear next step.")
        st.markdown(result.seller_response)
    if context.interactions:
        st.markdown("### Timeline")
        for item in reversed(context.interactions):
            st.markdown(f"**{item.type.title()}** — {item.summary}")
            if item.commitments:
                st.caption("Commitment: " + "; ".join(item.commitments))

with copilot_tab:
    st.subheader("Sales copilot")
    prompt = st.text_area("Ask about this account or deal", placeholder="What should I do before my next meeting?", height=140)
    mode = st.selectbox("Mode", ["Deal review", "Meeting prep", "Prospecting"])
    if st.button("Ask Sales GPT") and prompt.strip():
        workflow = {"Deal review": "deal-review", "Meeting prep": "meeting-prep", "Prospecting": "prospect"}[mode]
        result, context = run_workflow(account, workflow, prompt)
        st.markdown(result.seller_response)
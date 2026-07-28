from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from .memory import apply_result
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
    rows = []
    for name, field in context.meddpicc.model_dump().items():
        rows.append({
            "Dimension": name.replace("_", " ").title(),
            "Status": field["status"],
            "Value": str(field.get("value") or ""),
            "Next question": field.get("next_question") or "",
        })
    return rows


st.title("Sales GPT Agent")
st.caption("SDR + Account Executive + Sales Manager copilot")

account = st.sidebar.text_input("Account", placeholder="e.g. Acme Corp")
if not account:
    st.info("Enter an account name to open its sales workspace.")
    st.stop()

context = store.load(account)
st.sidebar.markdown(f"**Stage:** {context.opportunity.stage}")
st.sidebar.markdown(f"**ICP score:** {context.account.icp_score if context.account.icp_score is not None else 'Not scored'}")

research_tab, workspace_tab, transcript_tab, copilot_tab = st.tabs([
    "Research", "Deal Workspace", "Transcript", "Copilot"
])

with research_tab:
    st.subheader("Account research")
    research_request = st.text_area(
        "Research objective",
        value="Research this account, assess ICP fit, identify recent triggers, likely personas, sales hypotheses, and recommend the next action.",
        height=120,
    )
    if st.button("Research account", type="primary"):
        result, context = run_workflow(account, "research", research_request)
        st.markdown(result.seller_response)
        st.success("Account memory updated.")

    if context.account.signals:
        st.markdown("### Signals")
        for signal in context.account.signals:
            st.markdown(f"- {signal}")

with workspace_tab:
    col1, col2, col3 = st.columns(3)
    col1.metric("Stage", context.opportunity.stage)
    col2.metric("ICP", context.account.icp_score if context.account.icp_score is not None else "—")
    col3.metric("Stakeholders", len(context.stakeholders))

    st.markdown("### MEDDPICC")
    st.dataframe(meddpicc_rows(context), use_container_width=True, hide_index=True)

    left, right = st.columns(2)
    with left:
        st.markdown("### Stakeholders")
        if context.stakeholders:
            st.dataframe(
                [s.model_dump() for s in context.stakeholders],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No stakeholders mapped yet.")
    with right:
        st.markdown("### Next actions")
        if context.opportunity.next_actions:
            for action in context.opportunity.next_actions:
                st.markdown(f"- {action}")
        else:
            st.caption("No next actions yet.")
        st.markdown("### Risks")
        for risk in context.opportunity.risks:
            st.markdown(f"- {risk}")

    if st.button("Run deal review"):
        result, context = run_workflow(
            account,
            "deal-review",
            "Review the opportunity. Assess MEDDPICC, stakeholder coverage, deal risks, forecast quality, and recommend the three highest-leverage next actions.",
        )
        st.markdown(result.seller_response)

with transcript_tab:
    st.subheader("Analyze a sales call")
    uploaded = st.file_uploader("Upload transcript", type=["txt", "md"])
    pasted = st.text_area("Or paste transcript", height=260)
    if st.button("Analyze transcript", type="primary"):
        transcript = pasted
        if uploaded is not None:
            transcript = uploaded.getvalue().decode("utf-8")
        if not transcript.strip():
            st.warning("Add a transcript first.")
        else:
            result, context = run_workflow(
                account,
                "transcript",
                f"Analyze this sales-call transcript and update the opportunity evidence:\n\n{transcript}",
            )
            st.markdown(result.seller_response)
            st.success("MEDDPICC, stakeholders, risks, and next actions were saved when supported by evidence.")

with copilot_tab:
    st.subheader("Sales copilot")
    prompt = st.text_area(
        "Ask about this account or deal",
        placeholder="What are the biggest gaps in this deal and what should I do before my next meeting?",
        height=140,
    )
    mode = st.selectbox("Mode", ["Deal review", "Meeting prep"])
    if st.button("Ask Sales GPT") and prompt.strip():
        workflow = "deal-review" if mode == "Deal review" else "meeting-prep"
        result, context = run_workflow(account, workflow, prompt)
        st.markdown(result.seller_response)
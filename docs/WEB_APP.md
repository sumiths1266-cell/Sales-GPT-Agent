# Sales GPT Web App

The Streamlit workspace turns the SDR + AE engine into an account-centric sales application.

## Run

```bash
pip install -e .
cp .env.example .env
# add OPENAI_API_KEY
streamlit run src/sales_gpt/web.py
```

## Workspace

### Research
Enter an account and run live research. The agent uses SDR account research, ICP scoring, and trigger-detection skills. Supported findings are saved into account memory.

### Deal Workspace
Shows opportunity stage, ICP score, stakeholder count, MEDDPICC status, stakeholder data, risks, and recommended next actions. Run an on-demand manager-style deal review from the same screen.

### Transcript
Upload or paste a sales-call transcript. The AE agent extracts buyer evidence and can update MEDDPICC, stakeholders, opportunity risks, unknowns, and next actions.

### Copilot
Ask account/deal questions using either Deal Review or Meeting Prep mode. The copilot reads the account's persistent context before responding.

## Current data model
Each account is persisted locally as JSON under `.sales-gpt/`. This is suitable for development and single-user use. A production version should move storage to a database and add authentication, organizations/users, audit history, CRM sync, and permissions.

## Product direction
The UI is intentionally account-centric rather than chatbot-centric. Chat is one capability inside the workspace; the durable product is the account/deal memory and the SDR/AE skills operating on it.
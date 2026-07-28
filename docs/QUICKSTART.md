# Quickstart

## 1. Install

```bash
git clone https://github.com/sumiths1266-cell/Sales-GPT-Agent.git
cd Sales-GPT-Agent
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -e .
cp .env.example .env
```

Add your OpenAI API key to `.env`.

## 2. Run SDR research

```bash
sales-gpt research "Acme Corp"
```

You can provide a more specific request:

```bash
sales-gpt research "Acme Corp" --request "Assess this account for an enterprise data platform sale and tell me who I should target first."
```

## 3. Prepare a meeting

```bash
sales-gpt meeting-prep "Acme Corp" --request "I am meeting the VP of Data tomorrow. Prepare discovery."
```

## 4. Analyze a call

Save a transcript as `call.txt`, then:

```bash
sales-gpt analyze-transcript "Acme Corp" call.txt
```

## 5. Review a deal

```bash
sales-gpt deal-review "Acme Corp"
```

## Current architecture

The CLI loads the shared account/opportunity context, selects a workflow, combines the relevant SDR/AE/manager markdown skills, and sends the playbook + seller request + context to the OpenAI Responses API.

Local account state is stored as JSON under `.sales-gpt/` by default.

## Important current limitation

The first runnable version can read persistent context but does not yet automatically write structured findings from model responses back into account memory. The next milestone should add structured response schemas, memory updates, web/CRM/email integrations, tests, and an interactive UI.
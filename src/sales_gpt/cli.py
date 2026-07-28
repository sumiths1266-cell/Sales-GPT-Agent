from __future__ import annotations

from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from .orchestrator import SalesOrchestrator
from .store import ContextStore

load_dotenv()
app = typer.Typer(help="Sales GPT Agent — SDR + Account Executive copilot")
console = Console()


def execute(account: str, workflow: str, request: str) -> None:
    store = ContextStore()
    context = store.load(account)
    result = SalesOrchestrator().run(workflow, context, request)
    console.print(Markdown(result))


@app.command()
def research(account: str, request: str = "Research this account, assess ICP fit, identify triggers, and recommend the next action.") -> None:
    execute(account, "research", request)


@app.command("meeting-prep")
def meeting_prep(account: str, request: str = "Prepare me for the meeting. Focus on hypotheses to test, discovery questions, stakeholders, and the desired buyer commitment.") -> None:
    execute(account, "meeting-prep", request)


@app.command("analyze-transcript")
def analyze_transcript(account: str, transcript: Path) -> None:
    text = transcript.read_text(encoding="utf-8")
    execute(account, "transcript", f"Analyze this sales-call transcript:\n\n{text}")


@app.command("deal-review")
def deal_review(account: str, request: str = "Review this opportunity, assess MEDDPICC, risks, forecast, and tell me the three highest-leverage next actions.") -> None:
    execute(account, "deal-review", request)


if __name__ == "__main__":
    app()
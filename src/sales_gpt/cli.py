from __future__ import annotations

from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from .memory import apply_result
from .orchestrator import SalesOrchestrator
from .store import ContextStore

load_dotenv()
app = typer.Typer(help="Sales GPT Agent — SDR + Account Executive copilot")
console = Console()


def execute(account: str, workflow: str, request: str, save: bool = True) -> None:
    store = ContextStore()
    context = store.load(account)
    result = SalesOrchestrator().run(workflow, context, request)
    console.print(Markdown(result.seller_response))
    if save:
        updated = apply_result(context, result)
        path = store.save(updated)
        console.print(f"\n[dim]Memory updated: {path}[/dim]")


@app.command()
def research(
    account: str,
    request: str = "Research this account, assess ICP fit, identify triggers, and recommend the next action.",
    save: bool = True,
) -> None:
    execute(account, "research", request, save)


@app.command("meeting-prep")
def meeting_prep(
    account: str,
    request: str = "Prepare me for the meeting. Focus on hypotheses to test, discovery questions, stakeholders, and the desired buyer commitment.",
    save: bool = True,
) -> None:
    execute(account, "meeting-prep", request, save)


@app.command("analyze-transcript")
def analyze_transcript(account: str, transcript: Path, save: bool = True) -> None:
    text = transcript.read_text(encoding="utf-8")
    execute(account, "transcript", f"Analyze this sales-call transcript:\n\n{text}", save)


@app.command("deal-review")
def deal_review(
    account: str,
    request: str = "Review this opportunity, assess MEDDPICC, risks, forecast, and tell me the three highest-leverage next actions.",
    save: bool = True,
) -> None:
    execute(account, "deal-review", request, save)


if __name__ == "__main__":
    app()
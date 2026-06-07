from pathlib import Path
import sys

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from src.ingestion.logs import ingest_from_paths, ingest_from_stdin
from src.orchestrator import TroubleshootingOrchestrator

load_dotenv()

if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
app = typer.Typer(
    name="devops-agent",
    help="Elite DevOps SRE Troubleshooting Agent — OODA-loop multi-agent RCA.",
    no_args_is_help=True,
)
console = Console()


@app.command("analyze")
def analyze(
    logs: list[Path] = typer.Option(
        ..., "--log", "-l", help="Log file(s) to ingest. Pass multiple times for multiple files."
    ),
    metrics: Path | None = typer.Option(None, "--metrics", "-m", help="Metrics or alert dump"),
    ci: Path | None = typer.Option(None, "--ci", help="CI/CD pipeline failure output"),
    description: str = typer.Option("", "--desc", "-d", help="Human incident summary"),
    environment: str = typer.Option("production", "--env", "-e", help="Target environment"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write report to file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress OODA progress output"),
) -> None:
    """Analyze log files and produce a structured incident report."""
    context = ingest_from_paths(
        logs,
        metrics_path=metrics,
        ci_path=ci,
        description=description,
        environment=environment,
    )
    _run_analysis(context, output=output, verbose=not quiet)


@app.command("stdin")
def stdin_cmd(
    description: str = typer.Option("", "--desc", "-d", help="Human incident summary"),
    environment: str = typer.Option("production", "--env", "-e", help="Target environment"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write report to file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress OODA progress output"),
) -> None:
    """Pipe logs via stdin: kubectl logs ... | python -m src.main stdin"""
    context = ingest_from_stdin(description=description, environment=environment)
    _run_analysis(context, output=output, verbose=not quiet)


def _run_analysis(context, *, output: Path | None, verbose: bool) -> None:
    try:
        orchestrator = TroubleshootingOrchestrator()
        report_md = orchestrator.investigate_and_format(context, verbose=verbose)
    except ValueError as exc:
        console.print(f"[red]Configuration error:[/red] {exc}")
        raise typer.Exit(1) from exc
    except Exception as exc:
        console.print(f"[red]Analysis failed:[/red] {exc}")
        raise typer.Exit(1) from exc

    if output:
        output.write_text(report_md, encoding="utf-8")
        console.print(f"[green]Report written to[/green] {output}")

    console.print()
    try:
        console.print(Markdown(report_md))
    except UnicodeEncodeError:
        # Fallback for Windows terminals that cannot render emoji/markdown
        sys.stdout.write(report_md + "\n")


def main() -> None:
    app()


if __name__ == "__main__":
    main()

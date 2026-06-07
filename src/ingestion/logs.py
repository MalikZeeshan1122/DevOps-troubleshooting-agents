import sys
from pathlib import Path

from src.models.incident import IncidentContext


def ingest_from_paths(
    log_paths: list[Path],
    *,
    metrics_path: Path | None = None,
    ci_path: Path | None = None,
    description: str = "",
    environment: str = "unknown",
) -> IncidentContext:
    logs_parts: list[str] = []
    source_files: list[str] = []

    for path in log_paths:
        content = _read_file(path)
        logs_parts.append(f"=== {path.name} ===\n{content}")
        source_files.append(str(path))

    metrics = _read_file(metrics_path) if metrics_path else ""
    ci_output = _read_file(ci_path) if ci_path else ""

    if metrics_path:
        source_files.append(str(metrics_path))
    if ci_path:
        source_files.append(str(ci_path))

    return IncidentContext(
        logs="\n\n".join(logs_parts),
        metrics=metrics,
        ci_output=ci_output,
        description=description,
        environment=environment,
        source_files=source_files,
    )


def ingest_from_stdin(
    *,
    description: str = "",
    environment: str = "unknown",
) -> IncidentContext:
    content = sys.stdin.read()
    return IncidentContext(
        logs=content,
        description=description,
        environment=environment,
        source_files=["<stdin>"],
    )


def ingest_from_string(
    logs: str,
    *,
    metrics: str = "",
    ci_output: str = "",
    description: str = "",
    environment: str = "unknown",
) -> IncidentContext:
    return IncidentContext(
        logs=logs,
        metrics=metrics,
        ci_output=ci_output,
        description=description,
        environment=environment,
    )


def _read_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8", errors="replace")

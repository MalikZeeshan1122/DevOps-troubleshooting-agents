from rich.console import Console
from rich.panel import Panel

from src.agents import (
    DifferentialDiagnosisAgent,
    RCAAgent,
    RemediationAgent,
    SymptomAnalyzerAgent,
)
from src.llm.client import LLMClient
from src.models.incident import (
    DifferentialDiagnosis,
    IncidentContext,
    IncidentReport,
    RemediationPlan,
    RootCauseAnalysis,
    SymptomAnalysis,
)
from src.output.formatter import format_incident_report

console = Console()


class TroubleshootingOrchestrator:
    """Coordinates the OODA loop across specialized SRE agents."""

    def __init__(self, llm: LLMClient | None = None) -> None:
        llm = llm or LLMClient()
        self.symptom_agent = SymptomAnalyzerAgent(llm)
        self.diagnosis_agent = DifferentialDiagnosisAgent(llm)
        self.rca_agent = RCAAgent(llm)
        self.remediation_agent = RemediationAgent(llm)

    def investigate(self, context: IncidentContext, *, verbose: bool = True) -> IncidentReport:
        if verbose:
            console.print(Panel("[bold]OODA Loop: Observe[/bold] — Symptom Analysis", style="cyan"))

        symptoms = self.symptom_agent.run(context, SymptomAnalysis)
        if verbose:
            console.print(f"  Symptom: {symptoms.symptom}")
            console.print(f"  Severity: {symptoms.severity.value} | Blast: {symptoms.blast_radius}")

        if verbose:
            console.print(Panel("[bold]OODA Loop: Orient[/bold] — Differential Diagnosis", style="yellow"))

        diagnosis = self.diagnosis_agent.run(
            context, DifferentialDiagnosis, symptoms=symptoms
        )
        if verbose:
            for h in diagnosis.hypotheses:
                console.print(f"  [{h.category}] {h.description} ({h.likelihood})")

        if verbose:
            console.print(Panel("[bold]OODA Loop: Decide[/bold] — Root Cause Isolation", style="magenta"))

        rca = self.rca_agent.run(
            context, RootCauseAnalysis, symptoms=symptoms, diagnosis=diagnosis
        )
        if verbose:
            console.print(f"  Primary cause: {rca.primary_cause}")
            console.print(f"  Confidence: {rca.confidence}")

        if verbose:
            console.print(Panel("[bold]OODA Loop: Act[/bold] — Remediation Planning", style="green"))

        remediation = self.remediation_agent.run(
            context, RemediationPlan, symptoms=symptoms, rca=rca
        )

        return IncidentReport(
            context=context,
            symptoms=symptoms,
            diagnosis=diagnosis,
            rca=rca,
            remediation=remediation,
        )

    def investigate_and_format(
        self, context: IncidentContext, *, verbose: bool = True
    ) -> str:
        report = self.investigate(context, verbose=verbose)
        return format_incident_report(report)

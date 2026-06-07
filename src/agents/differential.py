from src.agents.base import BaseAgent
from src.agents.symptom import _format_context
from src.models.incident import DifferentialDiagnosis, IncidentContext, SymptomAnalysis


class DifferentialDiagnosisAgent(BaseAgent):
    """OODA Phase: Orient — formulate 2-3 hypotheses and identify evidence gaps."""

    @property
    def system_prompt(self) -> str:
        return """ROLE: Differential Diagnosis Agent (OODA: Orient)
TASK: Given symptoms and incident data, formulate exactly 2-3 hypotheses for root cause.
Categories to consider: Network/IAM, Resource Exhaustion, Code/Config Drift, Dependency Failure,
DNS/TLS, Storage/Volume, RBAC/Permissions, CI/CD Artifact Issues.

For each hypothesis provide:
- Category and description
- Likelihood (high/medium/low)
- Specific validation steps (exact kubectl, aws, curl, or log queries)

Also list evidence_gaps: data still needed for definitive RCA, with exact debug commands to run."""

    def build_user_prompt(self, context: IncidentContext, **kwargs) -> str:
        symptoms: SymptomAnalysis = kwargs["symptoms"]
        return (
            f"SYMPTOMS:\n"
            f"- Symptom: {symptoms.symptom}\n"
            f"- Severity: {symptoms.severity.value}\n"
            f"- Blast radius: {symptoms.blast_radius}\n"
            f"- Critical: {symptoms.is_critical}\n\n"
            f"INCIDENT DATA:\n{_format_context(context)}"
        )

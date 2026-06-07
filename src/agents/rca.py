from src.agents.base import BaseAgent
from src.agents.symptom import _format_context
from src.models.incident import (
    DifferentialDiagnosis,
    IncidentContext,
    RootCauseAnalysis,
    SymptomAnalysis,
)


class RCAAgent(BaseAgent):
    """OODA Phase: Decide — isolate root cause using evidence and hypotheses."""

    @property
    def system_prompt(self) -> str:
        return """ROLE: Root Cause Analysis Agent (OODA: Decide)
TASK: Using symptoms, hypotheses, and available evidence, determine the definitive root cause.

Rules:
- Cite specific log lines, error codes, or metric values as evidence
- Invalidate hypotheses that evidence contradicts
- Set confidence to 'low' if evidence is insufficient — do not fabricate certainty
- Distinguish correlation from causation (e.g. pod restart ≠ OOM without OOMKilled event)"""

    def build_user_prompt(self, context: IncidentContext, **kwargs) -> str:
        symptoms: SymptomAnalysis = kwargs["symptoms"]
        diagnosis: DifferentialDiagnosis = kwargs["diagnosis"]

        hypothesis_block = "\n".join(
            f"- [{h.category}] {h.description} (likelihood: {h.likelihood})"
            for h in diagnosis.hypotheses
        )
        gaps_block = "\n".join(f"- {g}" for g in diagnosis.evidence_gaps)

        return (
            f"SYMPTOMS: {symptoms.symptom} | {symptoms.severity.value} | {symptoms.blast_radius}\n\n"
            f"HYPOTHESES:\n{hypothesis_block}\n\n"
            f"EVIDENCE GAPS:\n{gaps_block}\n\n"
            f"INCIDENT DATA:\n{_format_context(context)}"
        )

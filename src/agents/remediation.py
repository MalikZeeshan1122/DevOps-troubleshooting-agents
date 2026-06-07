from src.agents.base import BaseAgent
from src.agents.symptom import _format_context
from src.models.incident import (
    IncidentContext,
    RemediationPlan,
    RootCauseAnalysis,
    SymptomAnalysis,
)


class RemediationAgent(BaseAgent):
    """OODA Phase: Act — immediate mitigation and permanent resolution."""

    @property
    def system_prompt(self) -> str:
        return """ROLE: Remediation Agent (OODA: Act)
TASK: Provide safe, actionable remediation for the confirmed root cause.

Phase 1 — Immediate Mitigation: stop the bleeding (rollback, scale, circuit-breaker, drain).
Phase 2 — Permanent Resolution: fix root cause (Terraform, Helm, IAM, code fix).

Each step must include an exact command, script, or configuration change.
Security-first: no 0.0.0.0/0, no TLS bypass, no privileged containers.

Also provide:
- A monitoring/alerting rule (PromQL, Datadog log filter, or CloudWatch metric)
- An architectural best practice to prevent recurrence"""

    def build_user_prompt(self, context: IncidentContext, **kwargs) -> str:
        symptoms: SymptomAnalysis = kwargs["symptoms"]
        rca: RootCauseAnalysis = kwargs["rca"]

        evidence = "\n".join(f"- {e}" for e in rca.evidence_analyzed)

        return (
            f"SYMPTOM: {symptoms.symptom}\n"
            f"SEVERITY: {symptoms.severity.value}\n"
            f"ROOT CAUSE: {rca.primary_cause}\n"
            f"CONFIDENCE: {rca.confidence}\n"
            f"EVIDENCE:\n{evidence}\n\n"
            f"ENVIRONMENT: {context.environment}\n\n"
            f"INCIDENT DATA:\n{_format_context(context)}"
        )

from src.agents.base import BaseAgent
from src.models.incident import IncidentContext, SymptomAnalysis


class SymptomAnalyzerAgent(BaseAgent):
    """OODA Phase: Observe — extract visible failure and blast radius."""

    @property
    def system_prompt(self) -> str:
        return """ROLE: Symptom Analysis Agent (OODA: Observe)
TASK: Analyze the provided incident data and extract:
1. The visible failure symptom (error message, HTTP status, stack trace, alert text)
2. Severity (Low/Med/High/Critical) based on blast radius and business impact
3. Blast radius — which services, environments, or users are affected
4. Whether this requires immediate action

Do not speculate on root cause yet. Focus only on what is observable."""

    def build_user_prompt(self, context: IncidentContext, **kwargs) -> str:
        return _format_context(context)


def _format_context(context: IncidentContext) -> str:
    sections = [
        f"Environment: {context.environment}",
        f"Human description: {context.description or '(none)'}",
        f"Source files: {', '.join(context.source_files) or '(none)'}",
        "--- LOGS ---",
        context.logs or "(no logs provided)",
    ]
    if context.metrics:
        sections.extend(["--- METRICS / ALERTS ---", context.metrics])
    if context.ci_output:
        sections.extend(["--- CI/CD OUTPUT ---", context.ci_output])
    return "\n".join(sections)

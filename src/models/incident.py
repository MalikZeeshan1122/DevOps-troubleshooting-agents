from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "Low"
    MEDIUM = "Med"
    HIGH = "High"
    CRITICAL = "Critical"


class IncidentContext(BaseModel):
    """Raw inputs gathered before agent analysis."""

    logs: str = Field(description="Concatenated log content from all sources")
    metrics: str = Field(default="", description="Metrics, alerts, or dashboard snapshots")
    ci_output: str = Field(default="", description="CI/CD pipeline failure output")
    description: str = Field(default="", description="Human-provided incident summary")
    environment: str = Field(default="unknown", description="e.g. production, staging, dev")
    source_files: list[str] = Field(default_factory=list, description="Paths of ingested files")


class SymptomAnalysis(BaseModel):
    symptom: str = Field(description="Visible failure: error, status code, stack trace")
    severity: Severity
    blast_radius: str = Field(description="Affected services, environments, users")
    is_critical: bool = Field(description="Whether immediate action is required")


class Hypothesis(BaseModel):
    category: str = Field(description="e.g. Network/IAM, Resource Exhaustion, Code/Config Drift")
    description: str
    likelihood: str = Field(description="high, medium, or low")
    validation_steps: list[str] = Field(description="Commands or queries to validate this hypothesis")


class DifferentialDiagnosis(BaseModel):
    hypotheses: list[Hypothesis] = Field(min_length=2, max_length=3)
    evidence_gaps: list[str] = Field(
        description="Missing data needed for definitive RCA; exact commands to run"
    )


class RootCauseAnalysis(BaseModel):
    primary_cause: str = Field(description="Definitive underlying issue")
    evidence_analyzed: list[str] = Field(description="Specific log lines or metrics cited")
    invalidated_hypotheses: list[str] = Field(default_factory=list)
    confidence: str = Field(description="high, medium, or low — low if evidence is insufficient")


class RemediationStep(BaseModel):
    action: str = Field(description="Exact command, script, or configuration change")
    rationale: str = Field(default="")


class RemediationPlan(BaseModel):
    immediate_mitigation: list[RemediationStep] = Field(min_length=1)
    permanent_resolution: list[RemediationStep] = Field(min_length=1)
    monitoring_alert: str = Field(description="PromQL, Datadog filter, or CloudWatch alert to add")
    best_practice: str = Field(description="Architectural recommendation to prevent recurrence")


class IncidentReport(BaseModel):
    context: IncidentContext
    symptoms: SymptomAnalysis
    diagnosis: DifferentialDiagnosis
    rca: RootCauseAnalysis
    remediation: RemediationPlan

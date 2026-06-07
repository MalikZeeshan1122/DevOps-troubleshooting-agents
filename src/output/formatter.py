from src.models.incident import IncidentReport


def format_incident_report(report: IncidentReport) -> str:
    s = report.symptoms
    d = report.diagnosis
    r = report.rca
    m = report.remediation

    lines = [
        "### 🚨 Incident Overview",
        f"- **Symptom:** {s.symptom}",
        f"- **Severity & Blast Radius:** {s.severity.value} — {s.blast_radius}",
        "",
        "### 🔍 Root Cause Analysis (RCA)",
        f"- **Primary Cause:** {r.primary_cause}",
        f"- **Confidence:** {r.confidence}",
        "- **Evidence/Logs Analyzed:**",
    ]
    for evidence in r.evidence_analyzed:
        lines.append(f"  - {evidence}")

    if r.invalidated_hypotheses:
        lines.append("- **Invalidated Hypotheses:**")
        for inv in r.invalidated_hypotheses:
            lines.append(f"  - {inv}")

    lines.extend([
        "",
        "### 🧪 Differential Diagnosis (Hypotheses)",
    ])
    for i, h in enumerate(d.hypotheses, 1):
        lines.append(f"- **H{i} [{h.category}]** ({h.likelihood}): {h.description}")
        for step in h.validation_steps:
            lines.append(f"  - Validate: `{step}`")

    if d.evidence_gaps:
        lines.append("- **Evidence Gaps (run next):**")
        for gap in d.evidence_gaps:
            lines.append(f"  - {gap}")

    lines.extend([
        "",
        "### 🛠️ Remediation Actions",
        "#### Phase 1: Immediate Mitigation (Stop the bleeding)",
    ])
    for i, step in enumerate(m.immediate_mitigation, 1):
        lines.append(f"- **Step {i}:** {step.action}")
        if step.rationale:
            lines.append(f"  - *Rationale:* {step.rationale}")

    lines.extend([
        "",
        "#### Phase 2: Permanent Resolution (Fix the root cause)",
    ])
    for i, step in enumerate(m.permanent_resolution, 1):
        lines.append(f"- **Step {i}:** {step.action}")
        if step.rationale:
            lines.append(f"  - *Rationale:* {step.rationale}")

    lines.extend([
        "",
        "### 🛡️ Post-Mortem & Prevention",
        f"- **Monitoring/Alerting Rule:** {m.monitoring_alert}",
        f"- **Best Practice Recommendation:** {m.best_practice}",
    ])

    return "\n".join(lines)

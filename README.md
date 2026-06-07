# DevOps Troubleshooting Agents

Autonomous **DevOps / SRE incident analysis** using a multi-agent **OODA loop** (Observe → Orient → Decide → Act) and structured LLM outputs.

Four specialized agents collaborate on every incident:

| Agent | OODA Phase | Responsibility |
|---|---|---|
| **Symptom Analyzer** | Observe | Extract visible failure, severity, blast radius |
| **Differential Diagnosis** | Orient | Formulate 2–3 hypotheses + evidence gaps |
| **RCA Agent** | Decide | Isolate root cause with cited evidence |
| **Remediation Agent** | Act | Mitigation, permanent fix, monitoring, prevention |

## Quick Start

### 1. Prerequisites

- Python 3.11+
- OpenAI API key (or any OpenAI-compatible endpoint)

### 2. Local Setup

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -e .
```

### 3. Analyze an Incident

```bash
# From log files
devops-agent analyze -l samples/k8s-oom-incident.log --env production

# Multiple sources
devops-agent analyze \
  -l samples/k8s-oom-incident.log \
  --ci samples/ci-terraform-failure.log \
  --desc "Checkout 503s after payment-service restarts" \
  -o reports/incident-report.md

# Pipe logs from kubectl / CI
kubectl logs deployment/payment-service --tail=200 | devops-agent stdin --env production
```

### 4. Docker

```bash
cp .env.example .env   # set OPENAI_API_KEY

docker compose build
docker compose run --rm devops-agent analyze \
  -l samples/k8s-oom-incident.log \
  --env production \
  -o reports/report.md
```

## Output Format

Every analysis produces a structured markdown report:

```
🚨 Incident Overview
🔍 Root Cause Analysis (RCA)
🧪 Differential Diagnosis (Hypotheses)
🛠️ Remediation Actions (Phase 1 + Phase 2)
🛡️ Post-Mortem & Prevention
```

## Screenshots

Running the sample K8s OOM incident locally:

```powershell
devops-agent analyze -l samples/k8s-oom-incident.log --env production -o reports/report.md
```

**OODA loop progress and incident overview**

![OODA loop progress and incident overview](<Screenshot 2026-06-07 093741.png>)

**Root cause analysis and differential diagnosis**

![Root cause analysis and differential diagnosis](<Screenshot 2026-06-07 093812.png>)

**Remediation actions and post-mortem prevention**

![Remediation actions and post-mortem prevention](<Screenshot 2026-06-07 093823.png>)

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | **Required.** API key for LLM provider |
| `LLM_MODEL` | `gpt-4o-mini` | Model name |
| `OPENAI_BASE_URL` | — | Custom endpoint (Ollama, Azure, vLLM) |

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│ Log Ingestion│────▶│   Orchestrator  │────▶│  Formatter  │
│ (files/stdin)│     │   (OODA Loop)   │     │  (Markdown) │
└─────────────┘     └────────┬─────────┘     └─────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        Symptom Agent   Diagnosis Agent    RCA Agent
              │                │                │
              └────────────────┴────────────────┘
                               │
                               ▼
                      Remediation Agent
```

## Project Structure

```
src/
├── agents/          # Specialized SRE agents (symptom, diagnosis, RCA, remediation)
├── ingestion/       # Log file and stdin ingestion
├── llm/             # OpenAI + instructor structured output client
├── models/          # Pydantic schemas for typed agent responses
├── output/          # Markdown report formatter
├── orchestrator.py  # OODA loop coordinator
└── main.py          # CLI entry point
samples/             # Example incident logs for testing
```

## Security

Agents are prompted with a **security-first** policy:

- No `0.0.0.0/0` security group openings
- No TLS verification bypass
- No privileged/root container workarounds

## License

MIT

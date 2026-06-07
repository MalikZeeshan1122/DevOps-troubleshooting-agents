# Payment-Service OOM Incident — Remediation Runbook
# Incident: HTTP 503 checkout failures, OOMKilled exit 137, Java heap space
# Root cause: BatchProcessor loaded entire pending queue into memory at 512Mi limit

set -euo pipefail

NAMESPACE="${NAMESPACE:-production}"
DEPLOYMENT="payment-service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! kubectl config current-context &>/dev/null; then
  echo "ERROR: No Kubernetes cluster configured."
  echo ""
  echo "This repo's sample incident is for AI analysis only. Run locally with:"
  echo "  devops-agent analyze -l samples/k8s-oom-incident.log --env production -o reports/report.md"
  echo ""
  echo "To use this runbook, connect to a cluster first (minikube start, eks update-kubeconfig, etc.)."
  exit 1
fi

if ! kubectl cluster-info --request-timeout=10s &>/dev/null; then
  echo "ERROR: Cannot reach Kubernetes API (context: $(kubectl config current-context))."
  exit 1
fi

echo "Cluster: $(kubectl config current-context) | Namespace: ${NAMESPACE}"
echo ""
echo "=== Phase 1: Immediate Mitigation ==="

echo "[1/3] Scaling to zero to stop crash loop..."
kubectl scale deployment "$DEPLOYMENT" -n "$NAMESPACE" --replicas=0
kubectl rollout status deployment/"$DEPLOYMENT" -n "$NAMESPACE" --timeout=120s || true

echo "[2/3] Rolling back to last known-good revision..."
kubectl rollout undo deployment/"$DEPLOYMENT" -n "$NAMESPACE"

echo "[3/3] Restoring minimal capacity..."
kubectl scale deployment "$DEPLOYMENT" -n "$NAMESPACE" --replicas=1
kubectl rollout status deployment/"$DEPLOYMENT" -n "$NAMESPACE" --timeout=180s

echo ""
echo "=== Phase 2: Permanent Resolution ==="

echo "[1/3] Applying fixed deployment (768Mi limit, JVM heap capped, startup probe)..."
kubectl apply -f "$SCRIPT_DIR/payment-service-config.yaml"

echo "[2/3] Applying memory-based HPA..."
kubectl apply -f "$SCRIPT_DIR/hpa.yaml"

echo "[3/3] Applying Prometheus alert rules..."
kubectl apply -f "$SCRIPT_DIR/prometheus-alert.yaml"

echo ""
echo "=== Verification ==="
kubectl get pods -n "$NAMESPACE" -l app="$DEPLOYMENT" -o wide
kubectl top pods -n "$NAMESPACE" -l app="$DEPLOYMENT" 2>/dev/null || echo "(metrics-server not available)"
kubectl get hpa -n "$NAMESPACE" "$DEPLOYMENT"

echo ""
echo "Done. Deploy image acme/payment-service:1.4.1-fix-oom with BatchProcessor.java fix before scaling to 2+ replicas."

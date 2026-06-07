# Payment-Service OOM Incident — Remediation Runbook (PowerShell)
# Incident: HTTP 503 checkout failures, OOMKilled exit 137, Java heap space

$ErrorActionPreference = "Stop"
$Namespace = if ($env:NAMESPACE) { $env:NAMESPACE } else { "production" }
$Deployment = "payment-service"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Test-KubectlCluster {
    $contexts = kubectl config get-contexts -o name 2>$null
    $dockerDesktop = $contexts | Where-Object { $_ -match "docker-desktop" } | Select-Object -First 1

    if ($dockerDesktop -and (kubectl config current-context 2>$null) -ne $dockerDesktop) {
        Write-Host "Switching kubectl context to $dockerDesktop" -ForegroundColor DarkYellow
        kubectl config use-context $dockerDesktop | Out-Null
    }

    $context = kubectl config current-context 2>$null
    if (-not $context) {
        Write-Host "ERROR: No Kubernetes cluster configured." -ForegroundColor Red
        Write-Host ""
        Write-Host "kubectl has no current-context. The runbook needs a real cluster (EKS, GKE, minikube, kind, Docker Desktop K8s)."
        Write-Host ""
        Write-Host "This repo's sample incident is for AI analysis only. Run locally with:"
        Write-Host '  devops-agent analyze -l samples/k8s-oom-incident.log --env production -o reports/report.md'
        Write-Host ""
        Write-Host "To use this runbook, connect to a cluster first, e.g.:"
        Write-Host "  minikube start"
        Write-Host "  aws eks update-kubeconfig --name YOUR-CLUSTER --region YOUR-REGION"
        Write-Host "  az aks get-credentials --resource-group RG --name CLUSTER"
        exit 1
    }

    kubectl cluster-info --request-timeout=10s 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Cannot reach Kubernetes API (context: $context)." -ForegroundColor Red
        Write-Host "Start your cluster or fix kubeconfig, then retry."
        exit 1
    }

    Write-Host "Cluster: $context | Namespace: $Namespace" -ForegroundColor DarkGray
    Write-Host ""
}

Test-KubectlCluster

Write-Host "=== Phase 1: Immediate Mitigation ===" -ForegroundColor Cyan

Write-Host "[1/3] Scaling to zero to stop crash loop..."
kubectl scale deployment $Deployment -n $Namespace --replicas=0
kubectl rollout status deployment/$Deployment -n $Namespace --timeout=120s 2>$null

Write-Host "[2/3] Rolling back to last known-good revision..."
kubectl rollout undo deployment/$Deployment -n $Namespace

Write-Host "[3/3] Restoring minimal capacity..."
kubectl scale deployment $Deployment -n $Namespace --replicas=1
kubectl rollout status deployment/$Deployment -n $Namespace --timeout=180s

Write-Host ""
Write-Host "=== Phase 2: Permanent Resolution ===" -ForegroundColor Cyan

Write-Host "[1/3] Applying fixed deployment..."
kubectl apply -f "$ScriptDir/payment-service-config.yaml"

Write-Host "[2/3] Applying memory-based HPA..."
kubectl apply -f "$ScriptDir/hpa.yaml"

Write-Host "[3/3] Applying Prometheus alert rules (skipped if Prometheus Operator not installed)..."
$prevEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
kubectl apply -f "$ScriptDir/prometheus-alert.yaml" 2>$null | Out-Null
$prometheusOk = ($LASTEXITCODE -eq 0)
$ErrorActionPreference = $prevEap
if (-not $prometheusOk) {
    Write-Host "  (skipped - install Prometheus Operator for alerting, or ignore for local demo)" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "=== Verification ===" -ForegroundColor Green
kubectl get pods -n $Namespace -l "app=$Deployment" -o wide
kubectl top pods -n $Namespace -l "app=$Deployment" 2>$null
kubectl get hpa -n $Namespace $Deployment

Write-Host ""
Write-Host "Done. Deploy image acme/payment-service:1.4.1-fix-oom with BatchProcessor fix before scaling to 2+ replicas."

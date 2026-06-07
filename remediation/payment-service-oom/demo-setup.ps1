# Deploy a demo payment-service so the remediation runbook has something to fix.
# Requires Docker Desktop Kubernetes (context: docker-desktop).

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$context = kubectl config current-context 2>$null
if (-not $context) {
    Write-Host "ERROR: No kubectl context. Start Docker Desktop and enable Kubernetes first." -ForegroundColor Red
    exit 1
}

Write-Host "Using cluster context: $context" -ForegroundColor Cyan
Write-Host "Deploying demo broken payment-service to namespace 'production'..." -ForegroundColor Cyan

kubectl apply -f "$ScriptDir/demo-broken-deployment.yaml"
kubectl rollout status deployment/payment-service -n production --timeout=120s

# Create a second revision so 'kubectl rollout undo' works in the runbook
kubectl set image deployment/payment-service payment-service=nginx:1.26-alpine -n production
kubectl rollout status deployment/payment-service -n production --timeout=120s

Write-Host ""
Write-Host "Demo ready. Current pods:" -ForegroundColor Green
kubectl get pods -n production -l app=payment-service -o wide

Write-Host ""
Write-Host "Now run the remediation runbook:" -ForegroundColor Yellow
Write-Host "  .\remediation\payment-service-oom\runbook.ps1"

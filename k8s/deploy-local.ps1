# Despliegue LOCAL en el Kubernetes de Docker Desktop.
# Requisito: Docker Desktop con Kubernetes habilitado (Settings > Kubernetes > Enable).
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
Set-Location $root

Write-Host "== Contexto de Kubernetes ==" -ForegroundColor Cyan
kubectl config use-context docker-desktop
kubectl cluster-info | Select-Object -First 1

Write-Host "`n== [1/4] Construir la imagen ==" -ForegroundColor Yellow
docker build -t securetask-api:ci .

Write-Host "`n== [2/4] Aplicar manifiestos (rolling update) ==" -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl -n securetask rollout status deployment/securetask-api --timeout=150s

Write-Host "`n== [3/4] Estado del despliegue ==" -ForegroundColor Yellow
kubectl -n securetask get deploy,svc,pods -o wide

Write-Host "`n== [4/4] Demostrar rolling update sin downtime ==" -ForegroundColor Yellow
kubectl -n securetask rollout restart deployment/securetask-api
kubectl -n securetask rollout status deployment/securetask-api --timeout=120s
kubectl -n securetask rollout history deployment/securetask-api

Write-Host "`nListo. Para probar la app:" -ForegroundColor Green
Write-Host "  kubectl -n securetask port-forward svc/securetask-api 8080:80" -ForegroundColor Green
Write-Host "  -> http://localhost:8080/health  y  http://localhost:8080/docs" -ForegroundColor Green

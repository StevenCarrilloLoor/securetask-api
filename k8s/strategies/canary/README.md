# Estrategia Canary

Se libera la versión nueva a una **fracción** del tráfico (canary) mientras la mayoría
sigue en la versión estable. Con réplicas: 4 stable + 1 canary ≈ 20% del tráfico al canary.

## Aumentar gradualmente el canary
```bash
kubectl -n securetask scale deploy/securetask-api-canary --replicas=2   # ~33%
kubectl -n securetask scale deploy/securetask-api-canary --replicas=4   # ~50%
```
## Promover (todo a la versión nueva) o abortar
```bash
# Promover: escalar canary y retirar stable
kubectl -n securetask scale deploy/securetask-api-stable --replicas=0
# Abortar: retirar el canary
kubectl -n securetask scale deploy/securetask-api-canary --replicas=0
```
**Ventaja:** riesgo acotado, se observan métricas/errores del canary antes de promover.
Para control de tráfico por porcentaje exacto (no por réplicas) se usa un service mesh (Istio/Linkerd) o Argo Rollouts.

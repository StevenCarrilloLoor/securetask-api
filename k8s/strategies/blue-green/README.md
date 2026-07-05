# Estrategia Blue-Green

Se mantienen DOS entornos idénticos: **blue** (versión actual) y **green** (versión nueva).
El tráfico lo dirige el `Service` mediante su `selector`.

## Publicar la versión nueva (switch de tráfico)
```bash
kubectl apply -f deployment-green.yaml           # levantar green en paralelo
kubectl -n securetask rollout status deploy/securetask-api-green
kubectl -n securetask patch service securetask-api \
  -p '{"spec":{"selector":{"app":"securetask-api","version":"green"}}}'   # switch instantáneo
```
## Rollback (si algo falla)
```bash
kubectl -n securetask patch service securetask-api \
  -p '{"spec":{"selector":{"app":"securetask-api","version":"blue"}}}'    # volver a blue
```
**Ventaja:** corte instantáneo y rollback inmediato. **Costo:** duplica los recursos durante la transición.

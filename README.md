# SecureTask API — CI/CD con enfoque DevSecOps

Pipeline de **integración y despliegue continuo (CI/CD)** con **DevSecOps** sobre una API REST
real (**FastAPI**): la seguridad se integra en **todo** el ciclo —build, pruebas, SAST, DAST,
integridad del artefacto— y llega hasta el **despliegue en Kubernetes** con estrategias de despliegue.

> Proyecto Integrador Final · Procesos de Software (ISWZ 3205) · **Steven Carrillo**

![CI DevSecOps](https://github.com/StevenCarrilloLoor/securetask-api/actions/workflows/ci-devsecops.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)
![Kubernetes](https://img.shields.io/badge/deploy-Kubernetes-326CE5.svg)

---

## 1. Aplicación

API REST de gestión de tareas con autenticación **JWT**: registro/login, y CRUD + búsqueda de tareas.
Documentación interactiva (Swagger) en `/docs`. Health check en `/health`.

```
app/            código (core, models, schemas, crud, api)   ·   tests/  pruebas (pytest)
Dockerfile      imagen (usuario no root)                     ·   k8s/    manifiestos Kubernetes
.github/workflows/ci-devsecops.yml   pipeline CI/CD DevSecOps (8 jobs)
.semgrep.yml    reglas SAST propias (Semgrep)
```

## 2. Pipeline CI/CD DevSecOps (8 jobs)

Se ejecuta en cada `push`/`pull_request` a `main`:

| Job | Fase | Herramienta | Salida |
|---|---|---|---|
| **build-test** | CI | pytest | pruebas verdes |
| **codeql** | SAST | CodeQL v4 | alertas en *Security* |
| **semgrep** | SAST | Semgrep (+reglas propias) | SARIF (artefacto + *Security*) |
| **bandit** | SAST | Bandit | reporte TXT/JSON (artefacto) |
| **gitleaks** | Secretos | GitLeaks | secret scanning |
| **build-image** | Artefacto | Docker + Syft + SLSA | imagen GHCR + **SBOM** + **attestation** |
| **dast** | DAST | OWASP ZAP | reporte HTML/MD (artefacto) |
| **deploy-k8s** | Deploy | kind + kubectl | despliegue real + rolling update |

**Integridad del artefacto (cadena de suministro):** la imagen se publica con un **SBOM (SPDX)** y una
**attestation de procedencia SLSA** firmada por GitHub. Verificable con:
```bash
gh attestation verify oci://ghcr.io/stevencarrilloloor/securetask-api:latest --owner StevenCarrilloLoor
```

## 3. Despliegue en Kubernetes

Manifiestos en [`k8s/`](k8s): `Deployment` (RollingUpdate, `maxUnavailable: 0` → cero downtime,
pods no-root, sondas `/health`), `Service`, `Ingress`, `HPA` (2→6 réplicas) y `Secret`.

- **En CI:** el job `deploy-k8s` crea un cluster **kind**, carga la imagen, aplica los manifiestos,
  verifica el rollout y hace un smoke test.
- **En local (Docker Desktop):** habilita Kubernetes en Docker Desktop y ejecuta:
  ```bash
  docker build -t securetask-api:ci .
  kubectl apply -f k8s/namespace.yaml -f k8s/secret.yaml -f k8s/deployment.yaml -f k8s/service.yaml
  kubectl -n securetask rollout status deploy/securetask-api
  kubectl -n securetask port-forward svc/securetask-api 8080:80   # http://localhost:8080/health
  ```
  (o usa el script `k8s/deploy-local.ps1`).

### Estrategias de despliegue
- **Rolling Update** (implementada): reemplazo gradual sin downtime.
- **Blue-Green** y **Canary** (documentadas con manifiestos en [`k8s/strategies/`](k8s/strategies)).

## 4. Cómo ejecutarlo (local)

**Windows — un clic:** doble clic en **`EJECUTAR_APP.bat`** → crea el entorno, instala dependencias,
arranca el servidor y abre la documentación interactiva (Swagger) en `http://localhost:8000/docs`.

**Manual:**
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -q
uvicorn app.main:app --reload                          # http://localhost:8000/docs
# o con Docker:
docker compose up --build
```

## 5. Herramientas y su propósito

GitHub Actions (orquestador) · FastAPI + pytest (app y pruebas) · Docker + GHCR (artefacto) ·
CodeQL / Semgrep / Bandit (SAST) · GitLeaks (secretos) · OWASP ZAP (DAST) ·
Syft (SBOM) + attestation SLSA (integridad) · kind / kubectl / Kubernetes (despliegue).

## 6. Evidencias

- **Pipeline:** pestaña *Actions* (corridas del workflow).
- **SAST:** *Security → Code scanning* (CodeQL + Semgrep).
- **Integridad:** [attestations](https://github.com/StevenCarrilloLoor/securetask-api/attestations) del repositorio.
- **Artefactos descargables:** `semgrep-sast-report`, `bandit-sast-report`, `sbom-spdx`, `dast-zap-report`.

## 7. Licencia

MIT — ver [LICENSE](LICENSE).

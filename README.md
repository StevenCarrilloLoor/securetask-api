# SecureTask API — DevSecOps / SAST en CI

API REST de **gestión de tareas** construida con **FastAPI**, usada como caso de estudio de
**DevSecOps**: integra herramientas de **SAST (Static Application Security Testing)** dentro
de un **pipeline de Integración Continua** en GitHub Actions.

> Curso: Procesos de Software (ISWZ 3205) · P3 · **Steven Carrillo**
> Tarea: *Informe de cumplimiento DevOps con herramientas de gestión de vulnerabilidades.*

![CI DevSecOps](https://github.com/OWNER/securetask-api/actions/workflows/ci-devsecops.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)

---

## 1. ¿Qué hace la aplicación?

Un servicio REST con autenticación **JWT** que permite a cada usuario registrar, listar,
buscar, actualizar y eliminar sus tareas.

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Crear una cuenta |
| `POST` | `/api/v1/auth/login` | Obtener un token JWT |
| `POST` | `/api/v1/tasks` | Crear una tarea |
| `GET` | `/api/v1/tasks` | Listar mis tareas |
| `GET` | `/api/v1/tasks/search?q=...` | Buscar tareas por título |
| `GET/PATCH/DELETE` | `/api/v1/tasks/{id}` | Ver / actualizar / eliminar |
| `POST` | `/api/v1/tasks/{id}/export` | Exportar una tarea |
| `GET` | `/health` | Health check |

Documentación interactiva (Swagger) disponible en `/docs` al levantar el servicio.

## 2. Arquitectura del proyecto

```
securetask-api/
├── app/
│   ├── main.py            # App FastAPI + routers + lifespan
│   ├── core/              # config, base de datos, seguridad (JWT/hash)
│   ├── models/            # modelos SQLAlchemy (User, Task)
│   ├── schemas/           # esquemas Pydantic (validación E/S)
│   ├── crud/              # acceso a datos
│   └── api/               # dependencias + routers (auth, tasks)
├── tests/                 # pruebas con pytest (7 casos)
├── .github/workflows/     # pipeline CI DevSecOps (build, tests y SAST)
├── .semgrep.yml           # reglas SAST personalizadas (Semgrep)
├── Dockerfile             # imagen (usuario no root)
├── docker-compose.yml
└── requirements*.txt
```

## 3. Cómo ejecutarlo

**Local (Python 3.12+):**
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -q                                           # correr las pruebas
uvicorn app.main:app --reload                       # levantar la API -> http://localhost:8000/docs
```

**Con Docker:**
```bash
docker compose up --build     # http://localhost:8000/docs
```

---

## 4. Pipeline CI/CD con enfoque DevSecOps

El workflow [`.github/workflows/ci-devsecops.yml`](.github/workflows/ci-devsecops.yml) se ejecuta
en cada `push` y `pull_request` a `main`. Contiene 5 *jobs*:

| Job | Tipo | Qué hace |
|---|---|---|
| **build-test** | CI | Instala dependencias y corre `pytest` (calidad funcional). |
| **codeql** | **SAST** | Análisis semántico con **CodeQL**; resultados en la pestaña *Security → Code scanning*. |
| **semgrep** | **SAST** | **Semgrep** (reglas del registro + reglas propias); sube **SARIF como artefacto** y a Code Scanning. |
| **bandit** | **SAST** | **Bandit** (SAST de Python); sube reporte **TXT + JSON como artefacto**. |
| **gitleaks** | Secret Scanning | **GitLeaks** busca credenciales filtradas (bonus DevSecOps). |

## 5. Herramienta SAST elegida y por qué

Se eligió **CodeQL** como herramienta SAST principal, acompañada de **Semgrep** y **Bandit**
(la buena práctica —y la recomendación de clase— es correr **dos herramientas SAST** para
contrastar hallazgos y descartar falsos positivos: si ambas marcan lo mismo, la vulnerabilidad
es real).

- **CodeQL** — Motor SAST **nativo de GitHub**, estándar de la industria (lo usa el propio
  GitHub). Hace **análisis de flujo de datos (taint tracking)**: sigue el dato desde la entrada
  del usuario hasta el punto peligroso, por lo que detecta inyecciones con muy pocos falsos
  positivos. **Gratis para repositorios públicos** y sus alertas quedan integradas en la pestaña
  *Security*.
- **Semgrep** — SAST **rápido basado en patrones**, open source, con miles de reglas de la
  comunidad (`p/security-audit`, `p/python`) y **fácilmente extensible con reglas propias**
  (ver `.semgrep.yml`). Genera **SARIF**, ideal como artefacto.
- **Bandit** — SAST **específico de Python** (proyecto OpenStack), muy rápido y sin dependencias
  externas. Excelente para CWE típicas de Python (subprocess, hashing débil, SQL por concatenación).
- **GitLeaks** *(bonus)* — *Secret scanning*: detecta credenciales hardcodeadas en el código y el
  historial de Git.

## 6. Retroalimentación del SAST — hallazgos detectados

El código incluye, de forma controlada, vulnerabilidades **realistas** para demostrar la
detección. Las herramientas las reportan así:

| # | Vulnerabilidad | CWE | Archivo | Detectada por |
|---|---|---|---|---|
| 1 | **SQL Injection** (consulta con f-string) | CWE-89 | `app/crud/task.py` (`search_tasks`) | CodeQL, Semgrep, Bandit (B608) |
| 2 | **OS Command Injection** (`subprocess`, `shell=True`) | CWE-78 | `app/api/routes/tasks.py` (`export_task`) | CodeQL, Semgrep, Bandit (B602) |
| 3 | **Hash criptográfico débil** (MD5) | CWE-327 | `app/api/routes/tasks.py` | Semgrep, Bandit (B324) |
| 4 | **Secreto embebido por defecto** | CWE-798 | `app/core/config.py` (`SECRET_KEY`) | Semgrep (regla propia) |

**Remediación (cómo se corregiría):**

1. Usar **consultas parametrizadas** (bind params) en lugar de f-strings en el SQL.
2. Ejecutar procesos con `shell=False` y **lista de argumentos**, validando la entrada.
3. Reemplazar **MD5** por **SHA-256** (o `secrets.token_hex` si es un identificador).
4. Inyectar `SECRET_KEY` por **variable de entorno**; nunca dejar un valor por defecto en el código.

## 7. Evidencias y artefactos

- **Pipeline:** pestaña **Actions** del repositorio (corridas del workflow).
- **Alertas SAST:** pestaña **Security → Code scanning alerts** (CodeQL + Semgrep).
- **Artefactos descargables** (al final de cada corrida, sección *Artifacts*):
  `semgrep-sast-report` (SARIF + texto) y `bandit-sast-report` (TXT + JSON).

## 8. Licencia

Distribuido bajo licencia **MIT**. Ver [LICENSE](LICENSE).

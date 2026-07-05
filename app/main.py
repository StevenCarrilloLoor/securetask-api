"""SecureTask API — punto de entrada de la aplicación FastAPI."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import auth, tasks
from app.core.config import settings
from app.core.database import Base, engine
from app.models import task as _task  # noqa: F401  (registra el modelo en la metadata)
from app.models import user as _user  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API REST de gestión de tareas usada como caso de estudio DevSecOps (SAST en CI).",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "service": settings.PROJECT_NAME}


app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(tasks.router, prefix=settings.API_V1_PREFIX)

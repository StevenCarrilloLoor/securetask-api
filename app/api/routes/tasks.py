import hashlib
import subprocess

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import task as crud
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> TaskRead:
    return crud.create_task(db, user.id, data)


@router.get("", response_model=list[TaskRead])
def list_tasks(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[TaskRead]:
    return crud.list_tasks(db, user.id)


@router.get("/search")
def search_tasks(
    q: str = Query(..., min_length=1, description="Texto a buscar en el título"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    # Llama a crud.search_tasks, que contiene un SQL vulnerable a inyección
    # (hallazgo esperado por el SAST).
    return crud.search_tasks(db, user.id, q)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> TaskRead:
    task = crud.get_task(db, user.id, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int, data: TaskUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> TaskRead:
    task = crud.get_task(db, user.id, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    return crud.update_task(db, task, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    task = crud.get_task(db, user.id, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    crud.delete_task(db, task)


@router.post("/{task_id}/export")
def export_task(
    task_id: int,
    fmt: str = Query("txt", description="Formato del archivo"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    task = crud.get_task(db, user.id, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    # ------------------------------------------------------------------
    # HALLAZGOS ESPERADOS POR EL SAST:
    #  1) Uso de MD5 (hash débil, CWE-327) para generar un identificador.
    #  2) subprocess con shell=True e interpolación de datos -> Command
    #     Injection (CWE-78). Forma segura: shell=False y lista de args.
    # ------------------------------------------------------------------
    etag = hashlib.md5(str(task.id).encode()).hexdigest()  # noqa: S324
    filename = f"task_{task_id}.{fmt}"
    subprocess.run(f"echo '{task.title}' > /tmp/{filename}", shell=True)  # noqa: S602
    return {"file": filename, "etag": etag}

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, owner_id: int, data: TaskCreate) -> Task:
    task = Task(owner_id=owner_id, **data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(db: Session, owner_id: int) -> list[Task]:
    return list(db.execute(select(Task).where(Task.owner_id == owner_id)).scalars())


def get_task(db: Session, owner_id: int, task_id: int) -> Task | None:
    return db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
    ).scalar_one_or_none()


def update_task(db: Session, task: Task, data: TaskUpdate) -> Task:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


def search_tasks(db: Session, owner_id: int, q: str) -> list[dict]:
    # ------------------------------------------------------------------
    # HALLAZGO ESPERADO POR EL SAST: SQL Injection (CWE-89).
    # La consulta se construye concatenando la entrada del usuario `q`
    # directamente en el SQL. CodeQL la marca como py/sql-injection.
    # Forma segura: usar parámetros vinculados (bindparams).
    # ------------------------------------------------------------------
    sql = text(f"SELECT id, title, status FROM tasks "
               f"WHERE owner_id = {owner_id} AND title LIKE '%{q}%'")
    rows = db.execute(sql).fetchall()
    return [dict(r._mapping) for r in rows]

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import Task, User
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(
    prefix="/task",
    tags=["task"],
)


@router.get('/')
def all_tasks(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(Task)).all()
    return users


@router.get('/task_id')
def task_by_id(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.scalars(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")
    return task


@router.post('/create')
def create_task(task_data: CreateTask, user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    new_task = Task(
        title=task_data.title,
        slug=slugify(task_data.title),
        content=task_data.content,
        priority=task_data.priority,
        user_id=user.id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.put('/update')
def update_task(task_id: int, task_data: UpdateTask, db: Annotated[Session, Depends(get_db)]):
    task = db.scalars(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.execute(update(Task).where(Task.id == task_id).values(
        title=task_data.title,
        content=task_data.content,
        priority=task_data.priority,
    ))
    db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "User update is successful!"}


@router.delete('/delete')
def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.scalars(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "Task deleted"}

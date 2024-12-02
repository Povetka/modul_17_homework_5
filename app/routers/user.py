from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get("/")
def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get("/user_id")
def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
    return user


@router.get("/user_id/tasks")
def tasks_by_user_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    return tasks


@router.post("/create")
def create_user(user_data: CreateUser, db: Annotated[Session, Depends(get_db)]):
    new_user = User(
        username=user_data.username,
        slug=slugify(user_data.username),
        firstname=user_data.firstname,
        lastname=user_data.lastname,
        age=user_data.age,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.put("/update")
def update_user(user_id: int, user_data: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.execute(update(User).where(User.id == user_id).values(
        firstname=user_data.firstname,
        lastname=user_data.lastname,
        age=user_data.age,
    ))
    db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "User update is successful!"}


@router.delete("/delete")
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    for task in tasks:
        db.delete(task)

    db.delete(user)
    db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "User and related tasks deleted"}

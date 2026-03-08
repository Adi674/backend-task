from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskDelete
from app.core.dependencies import get_current_user, get_admin_user
from app.core.response import success_response, error_response

router = APIRouter()


# ─────────────────────────────────────────
# USER ROUTES — own tasks only
# ─────────────────────────────────────────

# Create a task
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_task = Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        owner_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return success_response(
        message="Task created successfully",
        data=TaskResponse.model_validate(new_task).model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED
    )


# Get all own tasks
@router.get("/")
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()

    if not tasks:
        return success_response(
            message="No tasks found, your task list is empty",
            data=[]
        )

    return success_response(
        message="Tasks fetched successfully",
        data=[TaskResponse.model_validate(t).model_dump(mode="json") for t in tasks]
    )


# Get single task — task_id in body
@router.get("/single")
def get_task(
    task_id: UUID,                              # ← query param ?task_id=...
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()

    if not task:
        return error_response(
            message="Task not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

    return success_response(
        message="Task fetched successfully",
        data=TaskResponse.model_validate(task).model_dump(mode="json")
    )


# Update task — task_id in request body
@router.put("/")
def update_task(
    payload: TaskUpdate,                        # ← task_id comes from body
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == payload.task_id,
        Task.owner_id == current_user.id
    ).first()

    if not task:
        return error_response(
            message="Task not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

    update_fields = payload.get_update_fields()

    if not update_fields:
        return error_response(
            message="No fields provided to update",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    for field, value in update_fields.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return success_response(
        message="Task updated successfully",
        data=TaskResponse.model_validate(task).model_dump(mode="json")
    )


# Delete task — task_id in request body
@router.delete("/")
def delete_task(
    payload: TaskDelete,                  # ← now request body
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == payload.task_id,       # ← from body now
        Task.owner_id == current_user.id
    ).first()

    if not task:
        return error_response(
            message="Task not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

    db.delete(task)
    db.commit()

    return success_response(
        message="Task deleted successfully",
        data=None
    )


# ─────────────────────────────────────────
# ADMIN ROUTES — access all tasks
# ─────────────────────────────────────────

# Admin — get all tasks from all users
@router.get("/admin/all")
def admin_get_all_tasks(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    tasks = db.query(Task).all()

    if not tasks:
        return success_response(
            message="No tasks found in the system",
            data=[]
        )

    return success_response(
        message="All tasks fetched successfully",
        data=[TaskResponse.model_validate(t).model_dump(mode="json") for t in tasks]
    )


# Admin — update any task — task_id in body
@router.put("/admin")
def admin_update_task(
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    task = db.query(Task).filter(Task.id == payload.task_id).first()

    if not task:
        return error_response(
            message="Task not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

    update_fields = payload.get_update_fields()

    if not update_fields:
        return error_response(
            message="No fields provided to update",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    for field, value in update_fields.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return success_response(
        message="Task updated by admin successfully",
        data=TaskResponse.model_validate(task).model_dump(mode="json")
    )


# Admin — delete any task — task_id in body
@router.delete("/admin")
def admin_delete_task(
    payload: TaskDelete,                  # ← now request body
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    task = db.query(Task).filter(
        Task.id == payload.task_id        # ← from body now
    ).first()

    if not task:
        return error_response(
            message="Task not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

    db.delete(task)
    db.commit()

    return success_response(
        message="Task deleted by admin successfully",
        data=None
    )
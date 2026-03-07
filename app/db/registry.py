# This file exists purely to register all models with Base
# Import this ONLY in main.py before create_all()
from app.db.base import Base
from app.models.user import User
from app.models.task import Task

__all__ = ["Base", "User", "Task"]
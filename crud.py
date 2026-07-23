from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import Optional, List, Tuple
from datetime import datetime
import schemas
import models


def get_task(db:Session, task_id:int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(
        db : Session,
        skip : int = 0,
        limit : int = 100,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None
) -> Tuple[List[models.Task], int]:
    

    query = db.query(models.Task)
    
    # Apply filters
    if completed is not None:
        query = query.filter(models.Task.completed == completed)

    if priority:
        priority_map = {"low": 1, "medium": 2, "high": 3}
        query = query.filter(models.Task.priority == priority_map.get(priority.lower(), 2))

    if category:
        query = query.filter(models.Task.category.ilike(f"%{category}%"))
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Task.title.ilike(search_term),
                models.Task.description.ilike(search_term)
            )
        )

    # Get total count
    total = query.count()

    # Apply pagination and order by created_at desc
    tasks = query.order_by(desc(models.Task.created_at)).offset(skip).limit(limit).all()

    return tasks, total


def create_task(db: Session, task: schemas.TaskCreate):
    # Convert priority enum to integer
    priority_map = {"low": 1, "medium": 2, "high": 3}
    db_task = models.Task(
        title=task.title,
        description=task.description,
        completed=task.completed,
        priority=priority_map.get(task.priority.value, 2),
        due_date=task.due_date,
        category=task.category
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Convert priority if provided
    if "priority" in update_data and update_data["priority"]:
        priority_map = {"low": 1, "medium": 2, "high": 3}
        update_data["priority"] = priority_map.get(update_data["priority"].value, 2)
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    db.delete(db_task)
    db.commit()
    return db_task

def delete_completed_tasks(db: Session):
    deleted = db.query(models.Task).filter(models.Task.completed == True).delete()
    db.commit()
    return deleted

def toggle_task_status(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    db_task.completed = not db_task.completed
    db_task.updated_at = datetime.now()
    db.commit()
    db.refresh(db_task)
    return db_task




def get_task_statistics(db: Session):
    total = db.query(models.Task).count()
    completed = db.query(models.Task).filter(models.Task.completed == True).count()
    pending = total - completed
    
    # Tasks by priority
    low_priority = db.query(models.Task).filter(models.Task.priority == 1).count()
    medium_priority = db.query(models.Task).filter(models.Task.priority == 2).count()
    high_priority = db.query(models.Task).filter(models.Task.priority == 3).count()
    
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_rate": (completed / total * 100) if total > 0 else 0,
        "by_priority": {
            "low": low_priority,
            "medium": medium_priority,
            "high": high_priority
        }
    }
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import models
import schemas
import crud
from database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Task Management API",
    description="A complete task/todo management API built with FastAPI",
    version="1.0.0"
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Task Management API",
        "docs": "/docs",
        "redoc": "/redoc"
    }



# Create a new task
@app.post(
    "/tasks/",
    response_model=schemas.Task,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task"
)
async def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new task with the following parameters:
    - **title**: Task title (required)
    - **description**: Task description (optional)
    - **completed**: Task completion status (default: false)
    - **priority**: Task priority (low, medium, high) (default: medium)
    - **due_date**: Due date for the task (optional)
    - **category**: Task category (optional)
    """
    return crud.create_task(db=db, task=task)



# Get all tasks with pagination and filtering
@app.get(
    "/tasks/",
    response_model=schemas.TaskListResponse,
    summary="Get all tasks with filters"
)
async def get_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of tasks to return"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[str] = Query(None, regex="^(low|medium|high)$", description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    db: Session = Depends(get_db)
):
    """
    Get all tasks with optional filters and pagination.
    
    - **skip**: Number of tasks to skip (for pagination)
    - **limit**: Maximum number of tasks to return
    - **completed**: Filter by completion status
    - **priority**: Filter by priority (low, medium, high)
    - **category**: Filter by category
    - **search**: Search in title and description
    """
    tasks, total = crud.get_tasks(
        db=db,
        skip=skip,
        limit=limit,
        completed=completed,
        priority=priority,
        category=category,
        search=search
    )
    
    pages = (total + limit - 1) // limit if total > 0 else 1
    
    return schemas.TaskListResponse(
        tasks=tasks,
        total=total,
        page=(skip // limit) + 1,
        pages=pages,
        limit=limit
    )

# Get a single task by ID
@app.get(
    "/tasks/{task_id}",
    response_model=schemas.Task,
    summary="Get a specific task"
)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific task by its ID.
    """
    task = crud.get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return task

# Update a task
@app.put(
    "/tasks/{task_id}",
    response_model=schemas.Task,
    summary="Update a task"
)
async def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a task. Only the fields provided will be updated.
    """
    task = crud.update_task(db=db, task_id=task_id, task_update=task_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return task

# Toggle task completion status
@app.patch(
    "/tasks/{task_id}/toggle",
    response_model=schemas.Task,
    summary="Toggle task completion status"
)
async def toggle_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    Toggle the completion status of a task.
    """
    task = crud.toggle_task_status(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return task

# Delete a task
@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task"
)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific task by its ID.
    """
    task = crud.delete_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return None

# Delete all completed tasks
@app.delete(
    "/tasks/completed/",
    summary="Delete all completed tasks"
)
async def delete_completed_tasks(
    db: Session = Depends(get_db)
):
    """
    Delete all completed tasks.
    """
    deleted_count = crud.delete_completed_tasks(db=db)
    return {
        "message": f"Successfully deleted {deleted_count} completed tasks",
        "deleted_count": deleted_count
    }

# Get task statistics
@app.get(
    "/statistics/",
    summary="Get task statistics"
)
async def get_statistics(
    db: Session = Depends(get_db)
):
    """
    Get statistics about all tasks.
    """
    return crud.get_task_statistics(db=db)

# Additional endpoints for categories
@app.get(
    "/categories/",
    summary="Get all unique categories"
)
async def get_categories(
    db: Session = Depends(get_db)
):
    """
    Get all unique task categories.
    """
    categories = db.query(models.Task.category).distinct().filter(
        models.Task.category.isnot(None)
    ).all()
    return {"categories": [cat[0] for cat in categories if cat[0]]}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "task-management-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
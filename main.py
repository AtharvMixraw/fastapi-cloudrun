from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import models, schemas
from database import SessionLocal, engine, Base

app = FastAPI(title="FastAPI Cloud Run Demo")

# Create tables with better error handling
try:
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to create tables: {e}")
    # Don't exit - let the app start and handle DB errors per request

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Hello from FastAPI on Cloud Run!"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.post("/todos/", response_model=schemas.TodoOut)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    try:
        db_todo = models.Todo(title=todo.title, description=todo.description)
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo
    except Exception as e:
        logger.error(f"Error creating todo: {e}")
        raise HTTPException(status_code=500, detail="Failed to create todo")

@app.get("/todos/", response_model=list[schemas.TodoOut])
def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        return db.query(models.Todo).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error reading todos: {e}")
        raise HTTPException(status_code=500, detail="Failed to read todos")

@app.get("/todos/{todo_id}", response_model=schemas.TodoOut)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    try:
        todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
        if todo is None:
            raise HTTPException(status_code=404, detail="Todo not found")
        return todo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading todo {todo_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to read todo")

@app.put("/todos/{todo_id}", response_model=schemas.TodoOut)
def update_todo(todo_id: int, updated: schemas.TodoCreate, db: Session = Depends(get_db)):
    try:
        todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
        if todo is None:
            raise HTTPException(status_code=404, detail="Todo not found")
        todo.title = updated.title
        todo.description = updated.description
        db.commit()
        db.refresh(todo)
        return todo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating todo {todo_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update todo")

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    try:
        todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
        if todo is None:
            raise HTTPException(status_code=404, detail="Todo not found")
        db.delete(todo)
        db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting todo {todo_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete todo")
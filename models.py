from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from database import Base



class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)
    category = Column(String(50), nullable=True)


    def __repr__(self):
        return f"<Task {self.title}>"

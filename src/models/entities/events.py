from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey,
    Float, Text, Table
)
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.dbconnection import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey("branches.id"))
    title = Column(String(255))
    description = Column(Text)
    event_date = Column(DateTime)

    branch = relationship("Branch", back_populates="events")


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"
    id = Column(Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey("branches.id"))
    equipment = Column(String(100))
    description = Column(Text)
    status = Column(String(50), default="open")
    logged_at = Column(DateTime, default=datetime.utcnow)

    branch = relationship("Branch")
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey,
    Float, Text, Table
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.dbconnection import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    query = Column(Text)
    response = Column(Text)
    source = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)

    member = relationship("Member", back_populates="chat_sessions")
    reviews = relationship("HITLReview", back_populates="chat_session")


class StaffRole(Base):
    __tablename__ = "staff_roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(String(255))

    staff = relationship("Staff", back_populates="role")


class Staff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    branch_id = Column(Integer, ForeignKey("branches.id"))
    role_id = Column(Integer, ForeignKey("staff_roles.id"))

    branch = relationship("Branch", back_populates="staff")
    role = relationship("StaffRole", back_populates="staff")
    hitl_reviews = relationship("HITLReview", back_populates="reviewer")


class HITLReview(Base):
    __tablename__ = "hitl_reviews"
    id = Column(Integer, primary_key=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    reviewer_id = Column(Integer, ForeignKey("staff.id"))
    status = Column(String(50), default="pending")
    notes = Column(Text)
    reviewed_at = Column(DateTime)

    chat_session = relationship("ChatSession", back_populates="reviews")
    reviewer = relationship("Staff", back_populates="hitl_reviews")
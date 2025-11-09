from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey,
    Float, Text, Table
)
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.dbconnection import Base

class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    hashed_password = Column(String(255))
    membership_type = Column(String(50))
    join_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    loans = relationship("Loan", back_populates="member")
    fines = relationship("Fine", back_populates="member")
    reservations = relationship("Reservation", back_populates="member")
    reviews = relationship("Review", back_populates="member")
    chat_sessions = relationship("ChatSession", back_populates="member")


class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    issued_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    returned_date = Column(DateTime)

    member = relationship("Member", back_populates="loans")
    book = relationship("Book", back_populates="loans")


class Fine(Base):
    __tablename__ = "fines"
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    amount = Column(Float)
    reason = Column(String(255))
    status = Column(String(50), default="pending")
    issued_date = Column(DateTime, default=datetime.utcnow)

    member = relationship("Member", back_populates="fines")


class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    reserved_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="active")

    member = relationship("Member", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    rating = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    member = relationship("Member", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")
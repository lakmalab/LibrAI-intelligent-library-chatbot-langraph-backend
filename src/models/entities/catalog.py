from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey,
    Float, Text, Table
)
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.dbconnection import Base


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    nationality = Column(String(100))
    birth_year = Column(Integer)
    biography = Column(Text)

    books = relationship("Book", back_populates="author")


class Publisher(Base):
    __tablename__ = "publishers"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    country = Column(String(100))
    established = Column(Integer)

    books = relationship("Book", back_populates="publisher")


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    isbn = Column(String(20), unique=True)
    author_id = Column(Integer, ForeignKey("authors.id"))
    publisher_id = Column(Integer, ForeignKey("publishers.id"))
    shelf_id = Column(Integer, ForeignKey("shelves.id"))
    category = Column(String(100))
    total_copies = Column(Integer)
    available_copies = Column(Integer)
    published_year = Column(Integer)
    language = Column(String(50))

    author = relationship("Author", back_populates="books")
    publisher = relationship("Publisher", back_populates="books")
    shelf = relationship("Shelf", back_populates="books")
    loans = relationship("Loan", back_populates="book")
    reservations = relationship("Reservation", back_populates="book")
    reviews = relationship("Review", back_populates="book")
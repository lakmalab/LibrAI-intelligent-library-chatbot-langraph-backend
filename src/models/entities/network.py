from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey,
    Float, Text, Table
)
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.dbconnection import Base


class Chain(Base):
    __tablename__ = "chains"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    headquarters = Column(String(255))
    established_year = Column(Integer)

    branches = relationship("Branch", back_populates="chain")


class Branch(Base):
    __tablename__ = "branches"
    id = Column(Integer, primary_key=True)
    chain_id = Column(Integer, ForeignKey("chains.id"))
    name = Column(String(255), nullable=False)
    city = Column(String(100))
    address = Column(String(500))
    phone = Column(String(20))

    chain = relationship("Chain", back_populates="branches")
    sections = relationship("Section", back_populates="branch")
    staff = relationship("Staff", back_populates="branch")
    events = relationship("Event", back_populates="branch")


class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    branch_id = Column(Integer, ForeignKey("branches.id"))
    description = Column(Text)

    branch = relationship("Branch", back_populates="sections")
    shelves = relationship("Shelf", back_populates="section")


class Shelf(Base):
    __tablename__ = "shelves"
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True)
    section_id = Column(Integer, ForeignKey("sections.id"))
    capacity = Column(Integer)

    section = relationship("Section", back_populates="shelves")
    books = relationship("Book", back_populates="shelf")